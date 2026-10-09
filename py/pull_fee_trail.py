"""
USDC transfers and CCTP burns that follow the fees paid by the two groups.

Covers the fee recipient, the rewards distributor, the Safe, 0xb87f, 0x7e07, 0x6661, CCTP burns to 9Ns5 on Base and Ethereum, and USDC out of the cluster wallets.
Fee-module outflows are not pulled: nearly all are per-trade maker refunds (about 7M logs), and what a module passes on reaches the fee recipient, whose USDC is pulled in full.
Writes data/raw/base_transfers/fee_trail/<name>.parquet and provenance.json.
"""

import hashlib, json, os, datetime

import pandas as pd

from py.hypersync import get_logs_chunked
from py.chain import (ROOT, TRANSFERS, END_BLOCK, PULL_FROM, CLUSTERS_FROM, USDC, TRANSFER, FEE_RECIPIENT, REWARDS,
                      SAFE, X7E07, X6661, B87F, MESSENGER)

DIR = os.path.join(TRANSFERS, "fee_trail")
PROGRESS = os.path.join(DIR, "progress.json")

DEPOSIT_FOR_BURN = "0x0c8c1cbdc5190613ebd485511d4e2812cfa45eecb79d845893331fedad5130a5"
TO_9NS5 = "ce974468377a3871883e252c6417785f2230336ebe3558d71d4485abf08b5660"   # 9Ns5's USDC account on Solana.
ETH_FROM, ETH_END = 23_500_000, 26_070_000   # Ethereum blocks, October 2025 to 2026-09-28.


def pad(a):
    return "0x" + "0" * 24 + a[2:]


def usdc(logs):
    return pd.DataFrame({
        "block": [int(l["blockNumber"], 16) for l in logs],
        "tx": [l["transactionHash"] for l in logs],
        "log_index": [int(l["logIndex"], 16) for l in logs],
        "frm": ["0x" + l["topics"][1][-40:] for l in logs],
        "to": ["0x" + l["topics"][2][-40:] for l in logs],
        "usdc": [int(l["data"], 16) / 1e6 for l in logs]}, columns=["block", "tx", "log_index", "frm", "to", "usdc"])


def cluster_wallets():
    return sorted(pd.read_csv(os.path.join(ROOT, "paper", "out", "a06_limitless_cluster_wallets.csv")).wallet)


def by_wallets(name, side, wallets, a, b, base=DIR):
    """USDC Transfers to (side 2) or from (side 1) `wallets`, saved per wallet set so only new wallets are pulled."""
    root = os.path.join(base, name + ".parts")
    os.makedirs(root, exist_ok=True)
    manifest = os.path.join(root, "sets.json")
    sets = json.load(open(manifest)) if os.path.exists(manifest) else {}
    missing = sorted(set(wallets) - {w for ws in sets.values() for w in ws})
    if missing:
        key = hashlib.sha1(",".join(missing).encode()).hexdigest()[:10]
        topics = [TRANSFER, None, None]
        topics[side] = [pad(w) for w in missing]
        get_logs_chunked(USDC, topics, a, b, os.path.join(root, key), usdc, progress=PROGRESS)
        sets[key] = missing
        with open(manifest, "w") as fh:
            json.dump(sets, fh, indent=0)
    d = pd.concat([pd.read_parquet(os.path.join(root, k, f)) for k in sets for f in os.listdir(os.path.join(root, k))
                   if f.endswith(".parquet")], ignore_index=True)
    return d[(d.to if side == 2 else d.frm).isin(wallets)]


def burns(logs, chain):
    """CCTP DepositForBurn events whose Solana recipient is 9Ns5."""
    rows = []
    for l in logs:
        d = l["data"][2:]
        if d[64:128] == TO_9NS5:
            rows.append({"chain": chain, "block": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                         "log_index": int(l["logIndex"], 16), "frm": "0x" + l["topics"][2][-40:], "amount": int(d[:64], 16) / 1e6})
    return pd.DataFrame(rows, columns=["chain", "block", "tx", "log_index", "frm", "amount"])


def main():
    wallets = cluster_wallets()
    small = [  # Name, topics, filter on the decoded rows.
        ("feerec_usdc_in", [TRANSFER, None, pad(FEE_RECIPIENT)], lambda d: d.to == FEE_RECIPIENT),
        ("feerec_usdc_out", [TRANSFER, pad(FEE_RECIPIENT)], lambda d: d.frm == FEE_RECIPIENT),
        ("rewards_usdc_in", [TRANSFER, None, pad(REWARDS)], lambda d: d.to == REWARDS),
        ("safe_usdc_out", [TRANSFER, pad(SAFE)], lambda d: d.frm == SAFE),
    ]
    prov = {}
    d = get_logs_chunked(USDC, small[0][1], PULL_FROM, END_BLOCK, os.path.join(DIR, "small.parts"), usdc, progress=PROGRESS,
                         more=[(USDC, t) for _, t, _ in small[1:]])
    for name, t, keep in small:
        x = d[keep(d)]
        x.to_parquet(os.path.join(DIR, name + ".parquet"), index=False)
        prov[name] = {"contract": USDC, "topics": t, "blocks": [PULL_FROM, END_BLOCK], "rows": len(x)}
        print(name, len(x), "rows", flush=True)

    hops = [
        ("safe_usdc_in", [TRANSFER, None, pad(SAFE)], lambda d: d.to == SAFE),
        ("rewards_usdc_out", [TRANSFER, pad(REWARDS)], lambda d: d.frm == REWARDS),
        ("x7e07_usdc_in", [TRANSFER, None, pad(X7E07)], lambda d: d.to == X7E07),
        ("x7e07_usdc_out", [TRANSFER, pad(X7E07)], lambda d: d.frm == X7E07),
        ("x6661_usdc_in", [TRANSFER, None, pad(X6661)], lambda d: d.to == X6661),
        ("x6661_usdc_out", [TRANSFER, pad(X6661)], lambda d: d.frm == X6661),
    ]
    d = get_logs_chunked(USDC, hops[0][1], PULL_FROM, END_BLOCK, os.path.join(DIR, "hops.parts"), usdc, progress=PROGRESS,
                         more=[(USDC, t) for _, t, _ in hops[1:]])
    for name, t, keep in hops:
        x = d[keep(d)]
        x.to_parquet(os.path.join(DIR, name + ".parquet"), index=False)
        prov[name] = {"contract": USDC, "topics": t, "blocks": [PULL_FROM, END_BLOCK], "rows": len(x)}
        print(name, len(x), "rows", flush=True)
    # The chain into 9Ns5: 0xb87f's USDC, and every CCTP burn from Base or Ethereum to 9Ns5's account.
    d = get_logs_chunked(USDC, [TRANSFER, None, pad(B87F)], PULL_FROM, END_BLOCK, os.path.join(DIR, "b87f.parts"), usdc,
                         progress=PROGRESS, more=[(USDC, [TRANSFER, pad(B87F)])])
    for name, keep in (("b87f_usdc_in", d.to == B87F), ("b87f_usdc_out", d.frm == B87F)):
        d[keep].to_parquet(os.path.join(DIR, name + ".parquet"), index=False)
        prov[name] = {"contract": USDC, "address": B87F, "blocks": [PULL_FROM, END_BLOCK], "rows": int(keep.sum())}
    base = get_logs_chunked(MESSENGER, [DEPOSIT_FOR_BURN], PULL_FROM, END_BLOCK, os.path.join(DIR, "burns_base.parts"),
                            lambda logs: burns(logs, "Base"), progress=PROGRESS)
    eth = get_logs_chunked(MESSENGER, [DEPOSIT_FOR_BURN], ETH_FROM, ETH_END, os.path.join(DIR, "burns_eth.parts"),
                           lambda logs: burns(logs, "Ethereum"), progress=PROGRESS, url="https://eth.hypersync.xyz")
    d = pd.concat([base, eth], ignore_index=True)
    d.to_parquet(os.path.join(DIR, "burns_to_9ns5.parquet"), index=False)
    prov["burns_to_9ns5"] = {"contract": MESSENGER, "event": "DepositForBurn", "mint_recipient": TO_9NS5,
                             "blocks": {"Base": [PULL_FROM, END_BLOCK], "Ethereum": [ETH_FROM, ETH_END]}, "rows": len(d)}
    print("burns_to_9ns5", len(d), "rows", flush=True)

    d = by_wallets("cluster_usdc_out", 1, wallets, CLUSTERS_FROM, END_BLOCK)
    d.to_parquet(os.path.join(DIR, "cluster_usdc_out.parquet"), index=False)
    prov["cluster_usdc_out"] = {"contract": USDC, "topics": f"Transfer from {len(wallets)} cluster wallets",
                                "blocks": [CLUSTERS_FROM, END_BLOCK], "rows": len(d)}
    print("cluster_usdc_out", len(d), "rows", flush=True)
    json.dump({"pulled_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "source": "Envio HyperSync, Base and Ethereum", "pulls": prov},
              open(os.path.join(DIR, "provenance.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
