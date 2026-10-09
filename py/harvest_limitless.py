"""
Every Limitless order-book fill on Base, from the OrderFilled logs of its exchange contracts.

Logs come from Envio HyperSync when ENVIO_API_TOKEN is set, else from Coinbase's public RPC.
Writes raw logs and exchanges_verify.json to data/raw/limitless/, and data/norm/limitless_fills.parquet and limitless_tokens.parquet.
Usage: `python -m py.harvest_limitless [verify|harvest|normalize] [--start 2024-12-01]`.
"""

import argparse, datetime as dt, gzip, hashlib, json, os, sys, time, urllib.error, urllib.request

import pandas as pd
from tqdm import tqdm

from py import hypersync
from py.chain import (DATA, NORM, RPCS, SPAN0, SPAN_MAX, GROW_BELOW, BASE_GENESIS, CHUNK, END_BLOCK, EXCHANGES,
                      FEE_MODULES)

RAW = os.path.join(DATA, "raw", "limitless")

# Addresses `verify` checks as operator and admin of every exchange.
PROBES = {
    "deployer": "0xaae78342a756d5dca4319ede5b36ebdbf4a1b47c",
    "deployer_2024": "0xb260a005cfbad260bd77e1d34813e5618ac1cb63",
    "match_sender": "0x5d4142b27134f15b7a6c16f91104d9e4b7501f9e",
    "fee_module": FEE_MODULES[6],
}

ORDER_FILLED = "0xd0a08e8c493f9c94f29311604c9de1b4e8c8d4c06bd0c789af57f2d65bfec0f6"
TOKEN_REGISTERED = "0xbc9a2432e8aeb48327246cddd6e872ef452812b4243c04e6bfb786a2cd8faf0d"
SELECTORS = {"isOperator": "0x6d70f7ae", "isAdmin": "0x24d7806c",
             "getCollateral": "0x5c1548fb", "getCtf": "0x3b521d78"}


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _block_at(ts):
    return (int(ts) - BASE_GENESIS) // 2


def _date_block(date):
    return _block_at(dt.datetime.fromisoformat(date).replace(tzinfo=dt.timezone.utc).timestamp())


class Rpc:
    """JSON-RPC over the public endpoints, rotating and backing off when one refuses."""

    def __init__(self):
        self.i, self.span = 0, SPAN0

    @property
    def url(self):
        return RPCS[self.i]

    def call(self, method, params, tries=12):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        for attempt in range(tries):
            req = urllib.request.Request(self.url, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "countRS-research"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    out = json.load(r)
                if "error" not in out:
                    return out["result"]
                last = RuntimeError(out["error"])
                wait = min(60, 2 ** attempt)
            except urllib.error.HTTPError as e:
                last = e
                if e.code == 413:           # Response too large for this range: the caller shrinks it.
                    raise
                wait = min(60, 2 ** attempt)
                if e.code == 400 and b"too large" in e.read().lower():
                    raise
            except Exception as e:          # Dropped connections, truncated or malformed bodies.
                last = e
                wait = min(60, 2 ** attempt)
            self.i = (self.i + 1) % len(RPCS)
            time.sleep(wait)
        raise RuntimeError(f"{method} failed after {tries} tries: {last}")


def _word(addr):
    return "0x" + addr[2:].lower().rjust(64, "0")


def verify(rpc):
    at = hex(END_BLOCK)
    out = {"pulled_at": _now(), "rpc": RPCS, "block": END_BLOCK, "exchanges": {}}
    for ex, why in EXCHANGES.items():
        row = {"why": why}
        for fn in ("getCollateral", "getCtf"):
            row[fn] = "0x" + rpc.call("eth_call", [{"to": ex, "data": SELECTORS[fn]}, at])[-40:]
        for fn in ("isOperator", "isAdmin"):
            row[fn] = {name: int(rpc.call("eth_call", [{"to": ex, "data": SELECTORS[fn] + _word(a)[2:]},
                                                       at]), 16)
                       for name, a in PROBES.items()}
        out["exchanges"][ex] = row
        print(ex, json.dumps(row))
        time.sleep(0.5)
    os.makedirs(RAW, exist_ok=True)
    with open(os.path.join(RAW, "exchanges_verify.json"), "w") as fh:
        json.dump(out, fh, indent=1)


def _get_logs(rpc, q, a, b):
    """Logs for eth_getLogs query q over [a, b], from HyperSync when available, else from the public RPCs."""
    if hypersync.available():
        return hypersync.get_logs(q.get("address"), q["topics"], a, b)
    got, lo = [], a
    while lo <= b:
        hi = min(b, lo + rpc.span - 1)
        while True:
            try:
                page = rpc.call("eth_getLogs", [dict(q, fromBlock=hex(lo), toBlock=hex(hi))], tries=4)
                break
            except (urllib.error.HTTPError, RuntimeError) as e:
                # A node that keeps refusing a range is usually refusing its size, so split it.
                print(f"  {lo}-{hi}: {str(e)[:160]}", flush=True)
                if hi == lo:
                    raise
                hi = lo + (hi - lo) // 2
                rpc.span = max(50, hi - lo + 1)
        got.extend(page)
        if len(page) < GROW_BELOW:
            rpc.span = min(SPAN_MAX, rpc.span * 2)
        lo = hi + 1
        rpc.i = (rpc.i + 1) % len(RPCS)             # Alternate endpoints to spread the rate limit.
        time.sleep(0.15)
    return got


def harvest(rpc, start):
    """500k-block chunks into RAW/logs, the last one ending at END_BLOCK."""
    os.makedirs(os.path.join(RAW, "logs"), exist_ok=True)
    head = int(rpc.call("eth_blockNumber", []), 16)
    a, b = _date_block(start), min(END_BLOCK, head - 300)
    prov_path = os.path.join(RAW, "logs_provenance.jsonl")
    for c0 in tqdm(range(a - a % CHUNK, b + 1, CHUNK), unit="chunk", desc="harvest"):
        c1 = min(c0 + CHUNK - 1, b)
        path = os.path.join(RAW, "logs", f"{c0:09d}_{c1:09d}.jsonl.gz")
        if os.path.exists(path):
            continue
        t = time.time()
        logs = _get_logs(rpc, {"address": list(EXCHANGES), "topics": [[ORDER_FILLED, TOKEN_REGISTERED]]}, c0, c1)
        blob = "".join(json.dumps(l, sort_keys=True) + "\n" for l in logs).encode()
        with gzip.open(path + ".tmp", "wb") as f:
            f.write(blob)
        os.replace(path + ".tmp", path)
        prov = {"file": os.path.basename(path), "from_block": c0, "to_block": c1,
                "from_utc": dt.datetime.fromtimestamp(BASE_GENESIS + 2 * c0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "logs": len(logs), "sha256_uncompressed": hashlib.sha256(blob).hexdigest(),
                "source": hypersync.URL if hypersync.available() else RPCS, "addresses": list(EXCHANGES),
                "topics": [ORDER_FILLED, TOKEN_REGISTERED], "pulled_at": _now()}
        with open(prov_path, "a") as f:
            f.write(json.dumps(prov) + "\n")
        tqdm.write(f"{prov['from_utc'][:10]}  blocks {c0}-{c1}  {len(logs):>8} logs  {time.time() - t:5.0f}s")


def _words(data):
    d = data[2:]
    return [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]


def normalize():
    """
    Raw logs up to END_BLOCK to data/norm/limitless_fills.parquet and limitless_tokens.parquet.

    One row per OrderFilled. `taker_leg` marks the taker order's own record (taker is the exchange), which restates the maker rows of the same match, so volume counts only rows where it is False.
    Asset id 0 is USDC. `shares` and `usdc` are in whole units; `price` is USDC per share.
    Every logs* directory under RAW is read, so a backfill kept beside logs/ must cover other exchanges or blocks.
    Each file becomes its own Arrow table to keep memory near the size of the output.
    """
    import pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq

    files = [os.path.join(RAW, d, n) for d in sorted(os.listdir(RAW)) if d.startswith("logs")
             and os.path.isdir(os.path.join(RAW, d))
             for n in sorted(os.listdir(os.path.join(RAW, d))) if n.endswith(".jsonl.gz")]
    parts, tokens = [], []
    cols = ["block", "tx", "log_index", "exchange", "order_hash", "maker", "taker", "token_id",
            "maker_side", "shares", "usdc", "fee_raw"]
    for path in tqdm(files, unit="file", desc="normalize"):
        rows = {c: [] for c in cols}
        with gzip.open(path, "rt") as f:
            for line in f:
                l = json.loads(line)
                t, blk = l["topics"], int(l["blockNumber"], 16)
                if blk > END_BLOCK:
                    continue
                if t[0] == TOKEN_REGISTERED:
                    tokens.append({"exchange": l["address"].lower(), "token0": str(int(t[1], 16)),
                                   "token1": str(int(t[2], 16)), "condition_id": t[3], "block": blk})
                    continue
                m_asset, t_asset, m_amt, t_amt, fee = _words(l["data"])
                maker_buys = m_asset == 0
                for c, v in (("block", blk), ("tx", l["transactionHash"]), ("log_index", int(l["logIndex"], 16)),
                             ("exchange", l["address"].lower()), ("order_hash", t[1]),
                             ("maker", "0x" + t[2][-40:]), ("taker", "0x" + t[3][-40:]),
                             ("token_id", str(t_asset if maker_buys else m_asset)),
                             ("maker_side", "BUY" if maker_buys else "SELL"),
                             ("shares", (t_amt if maker_buys else m_amt) / 1e6),
                             ("usdc", (m_amt if maker_buys else t_amt) / 1e6), ("fee_raw", float(fee))):
                    rows[c].append(v)
        if rows["block"]:
            parts.append(pa.table(rows).combine_chunks())
    tab = pa.concat_tables(parts)
    del parts
    ts = pc.add(pc.multiply(tab["block"], 2), BASE_GENESIS)
    tab = tab.append_column("ts", ts)
    tab = tab.append_column("taker_leg", pc.is_in(tab["taker"], value_set=pa.array(list(EXCHANGES))))
    tab = tab.append_column("price", pc.divide(tab["usdc"], tab["shares"]))
    tab = tab.append_column("time", pc.cast(pc.cast(ts, pa.timestamp("s")), pa.timestamp("s", tz="UTC")))
    tab = tab.sort_by([("block", "ascending"), ("log_index", "ascending")])
    os.makedirs(NORM, exist_ok=True)
    pq.write_table(tab, os.path.join(NORM, "limitless_fills.parquet"))
    pd.DataFrame(tokens).drop_duplicates().to_parquet(
        os.path.join(NORM, "limitless_tokens.parquet"), index=False)
    legs = pc.sum(tab["taker_leg"]).as_py()
    print(f"{tab.num_rows} fill rows ({tab.num_rows - legs} maker fills), {len(tokens)} token registrations")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("step", nargs="?", default="all", choices=["verify", "harvest", "normalize", "all"])
    p.add_argument("--start", default="2024-12-01")
    a = p.parse_args()
    rpc = Rpc()
    if a.step in ("verify", "all"):
        verify(rpc)
    if a.step in ("harvest", "all"):
        harvest(rpc, a.start)
    if a.step in ("normalize", "all"):
        normalize()


if __name__ == "__main__":
    sys.exit(main())
