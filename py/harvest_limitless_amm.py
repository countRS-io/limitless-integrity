"""
Every Limitless AMM trade on Base: FPMMBuy and FPMMSell logs of the markets its two FPMM factories created.

Factory addresses and the first block come from DefiLlama's adapter (paper/refs/sources/defillama_limitless_index.ts).
Writes markets.csv and raw logs to data/raw/limitless_amm/, and data/norm/limitless_amm_trades.parquet.
Usage: `python -m py.harvest_limitless_amm [markets|harvest|normalize] [--start 2024-04-01]`.
"""

import argparse, datetime as dt, gzip, hashlib, json, os, sys, time

import pandas as pd
from tqdm import tqdm

from py import hypersync
from py.chain import DATA, NORM, RPCS, BASE_GENESIS, CHUNK, END_BLOCK, flashloan_wallets
from py.harvest_limitless import Rpc, _date_block, _get_logs, _now, _words

RAW = os.path.join(DATA, "raw", "limitless_amm")

FACTORIES = ["0xc397d5d70cb3b56b26dd5c2824d49a96c4dabf50", "0x8e50578aca3c5e2ef5ed2aa4bd66429b5e44c16e"]
FIRST_BLOCK = 13549462

CREATION = "0x92e0912d3d7f3192cad5c7ae3b47fb97f9c465c1dd12a5c24fd901ddb3905f43"
BUY = "0x4f62630f51608fc8a7603a9391a5101e58bd7c276139366fc107dc3b67c3dcf8"
SELL = "0xadcf2a240ed9300d681d9a3f5382b6c1beed1b7e46643e0c7b42cbe6e2d766b4"
KINDS = {BUY: "buy", SELL: "sell"}


def markets(rpc):
    """Every market the two factories created, with its collateral and that token's decimals."""
    head = min(END_BLOCK, int(rpc.call("eth_blockNumber", []), 16) - 300)
    logs = _get_logs(rpc, {"address": FACTORIES, "topics": [CREATION]}, FIRST_BLOCK, head)
    rows = []
    for l in logs:
        rows.append({"fpmm": "0x" + l["data"][2:66][-40:], "factory": l["address"].lower(),
                     "creator": "0x" + l["topics"][1][-40:], "collateral": "0x" + l["topics"][3][-40:],
                     "block": int(l["blockNumber"], 16), "tx": l["transactionHash"]})
    m = pd.DataFrame(rows)
    def decimals(c):                              # None when the collateral has no decimals().
        r = rpc.call("eth_call", [{"to": c, "data": "0x313ce567"}, hex(head)])
        return int(r, 16) if r not in ("0x", "", None) else None
    dec = {c: decimals(c) for c in m.collateral.unique()}
    m["decimals"] = m.collateral.map(dec)
    os.makedirs(RAW, exist_ok=True)
    m.to_csv(os.path.join(RAW, "markets.csv"), index=False)
    json.dump({"pulled_at": _now(), "source": hypersync.URL if hypersync.available() else RPCS, "factories": FACTORIES, "from_block": FIRST_BLOCK,
               "to_block": head, "markets": len(m), "collateral_decimals": dec},
              open(os.path.join(RAW, "markets_provenance.json"), "w"), indent=1)
    print(f"{len(m)} markets, collateral {dec}")


def harvest(rpc, start):
    fp = set(pd.read_csv(os.path.join(RAW, "markets.csv")).fpmm)
    os.makedirs(os.path.join(RAW, "logs"), exist_ok=True)
    a = max(FIRST_BLOCK, _date_block(start))
    b = min(END_BLOCK, int(rpc.call("eth_blockNumber", []), 16) - 300)
    for c0 in tqdm(range(a - a % CHUNK, b + 1, CHUNK), unit="chunk", desc="harvest"):
        c1 = min(c0 + CHUNK - 1, b)
        path = os.path.join(RAW, "logs", f"{c0:09d}_{c1:09d}.jsonl.gz")
        if os.path.exists(path):
            continue
        t = time.time()
        # Trade logs are queried by topic across Base and kept only from Limitless markets.
        served = _get_logs(rpc, {"topics": [[BUY, SELL]]}, c0, c1)
        kept = [l for l in served if l["address"].lower() in fp]
        blob = "".join(json.dumps(l, sort_keys=True) + "\n" for l in kept).encode()
        with gzip.open(path + ".tmp", "wb") as f:
            f.write(blob)
        os.replace(path + ".tmp", path)
        prov = {"file": os.path.basename(path), "from_block": c0, "to_block": c1,
                "from_utc": dt.datetime.fromtimestamp(BASE_GENESIS + 2 * c0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "served": len(served), "kept": len(kept), "sha256_uncompressed": hashlib.sha256(blob).hexdigest(),
                "source": hypersync.URL if hypersync.available() else RPCS, "topics": [BUY, SELL], "pulled_at": _now()}
        with open(os.path.join(RAW, "logs_provenance.jsonl"), "a") as f:
            f.write(json.dumps(prov) + "\n")
        tqdm.write(f"{prov['from_utc'][:10]}  blocks {c0}-{c1}  kept {len(kept):>8} of {len(served):>8}  "
              f"{time.time() - t:5.0f}s")


def normalize():
    """
    Raw logs up to END_BLOCK to data/norm/limitless_amm_trades.parquet.

    Amounts are scaled by the collateral's decimals, which outcome tokens share; trades in markets whose collateral has no decimals() are left out and counted.
    `flashloan_listed` marks traders on DefiLlama's list of Limitless flash-loan wallets.
    """
    m = pd.read_csv(os.path.join(RAW, "markets.csv")).set_index("fpmm")
    listed = flashloan_wallets()
    trades, unscaled = [], 0
    for name in sorted(n for n in os.listdir(os.path.join(RAW, "logs")) if n.endswith(".jsonl.gz")):
        with gzip.open(os.path.join(RAW, "logs", name), "rt") as f:
            for line in f:
                l = json.loads(line)
                blk, addr = int(l["blockNumber"], 16), l["address"].lower()
                if l["topics"][0] not in KINDS or blk > END_BLOCK:
                    continue
                if pd.isna(m.loc[addr, "decimals"]):
                    unscaled += 1
                    continue
                sc = 10 ** int(m.loc[addr, "decimals"])
                amount, fee, tokens = _words(l["data"])
                trades.append({"block": blk, "ts": BASE_GENESIS + 2 * blk, "tx": l["transactionHash"],
                               "log_index": int(l["logIndex"], 16), "fpmm": addr, "kind": KINDS[l["topics"][0]],
                               "who": "0x" + l["topics"][1][-40:], "collateral_amount": amount / sc, "fee": fee / sc,
                               "outcome_index": int(l["topics"][2], 16), "outcome_tokens": tokens / sc})
    t = pd.DataFrame(trades).drop_duplicates(["tx", "log_index"])
    t["time"] = pd.to_datetime(t.ts, unit="s", utc=True)
    t["collateral"] = t.fpmm.map(m.collateral)
    t["flashloan_listed"] = t.who.isin(listed)
    os.makedirs(NORM, exist_ok=True)
    t.sort_values(["block", "log_index"]).to_parquet(os.path.join(NORM, "limitless_amm_trades.parquet"), index=False)
    print(f"{len(t)} trades ({t.flashloan_listed.sum()} by listed flash-loan wallets), {unscaled} left out: no decimals()")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("step", nargs="?", default="all", choices=["markets", "harvest", "normalize", "all"])
    p.add_argument("--start", default="2024-04-01")
    a = p.parse_args()
    rpc = Rpc()
    if a.step in ("markets", "all"):
        markets(rpc)
    if a.step in ("harvest", "all"):
        harvest(rpc, a.start)
    if a.step in ("normalize", "all"):
        normalize()


if __name__ == "__main__":
    sys.exit(main())
