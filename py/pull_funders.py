"""
Every Circle CCTP mint into the largest Limitless order-book wallets, decoded to show who funded them.

Candidates are wallets on at least 10M order-book contracts, the unlinked 2024 exchange left out.
Each mint's MessageReceived log gives the source domain, recipient, amount and depositor.
Writes data/raw/base_transfers/cctp_mints.parquet and a provenance file.
"""

import json, os, time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd, pyarrow.parquet as pq, requests

from py.hypersync import get_logs_chunked
from py.chain import NORM, TRANSFERS, END_BLOCK, PULL_FROM, RPCS, TRANSFER, UNLINKED, USDC

TRANSMITTER = "0x81d40f21f12a8f0e3252bccb954d722d4c464b64"
DOMAINS = {0: "Ethereum", 1: "Avalanche", 2: "OP", 3: "Arbitrum", 5: "Solana", 6: "Base", 7: "Polygon"}
MIN_CONTRACTS = 10_000_000


def candidates():
    pf = pq.ParquetFile(os.path.join(NORM, "limitless_fills.parquet"))
    acc = pd.Series(dtype=float)
    for i in range(pf.num_row_groups):
        g = pf.read_row_group(i, columns=["maker", "taker", "shares", "taker_leg", "exchange"]).to_pandas()
        g = g[~g.taker_leg & (g.exchange != UNLINKED)]
        acc = acc.add(g.groupby("maker").shares.sum(), fill_value=0).add(g.groupby("taker").shares.sum(), fill_value=0)
    return sorted(acc[acc >= MIN_CONTRACTS].index)


def receipt(tx, i):
    for k in range(8):
        try:
            r = requests.post(RPCS[(i + k) % 2], json={"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionReceipt",
                                                     "params": [tx]}, timeout=30).json()
            if r.get("result"):
                return r["result"]
        except Exception:
            pass
        time.sleep(1 + k)
    raise RuntimeError(tx)


def decode(tx, i):
    rows, r = [], receipt(tx, i)
    for l in r["logs"]:
        if l["address"].lower() != TRANSMITTER or len(l["data"]) < 2 + 64 * 4:
            continue
        d = l["data"][2:]
        body = d[64 * 4:]   # After sourceDomain, sender, offset and length; then version (4 bytes) and 32-byte fields.
        domain = int(d[:64], 16)
        rows.append({"tx": tx, "block": int(l["blockNumber"], 16), "sender": r["from"].lower(), "domain": domain, "chain": DOMAINS.get(domain, str(domain)),
                     "recipient": "0x" + body[8 + 64:8 + 128][-40:], "amount": int(body[8 + 128:8 + 192], 16) / 1e6,
                     "depositor": body[8 + 192:8 + 256]})
    return rows


def main():
    wallets = candidates()
    topic = ["0x" + "0" * 24 + w[2:] for w in wallets]
    mints = get_logs_chunked(USDC, [TRANSFER, "0x" + "0" * 64, topic], PULL_FROM, END_BLOCK, os.path.join(TRANSFERS, "cctp_mints.parts"),
                             lambda logs: pd.DataFrame({"tx": [l["transactionHash"] for l in logs]}, columns=["tx"]))
    txs = sorted(set(mints.tx))
    with ThreadPoolExecutor(6) as ex:
        out = pd.DataFrame([r for rs in ex.map(decode, txs, range(len(txs))) for r in rs])
    out = out[out.recipient.isin(wallets)]
    out.to_parquet(os.path.join(TRANSFERS, "cctp_mints.parquet"), index=False)
    json.dump({"candidates": len(wallets), "min_contracts": MIN_CONTRACTS, "blocks": [PULL_FROM, END_BLOCK], "mint_txs": len(txs),
               "rows": len(out), "source": "Envio HyperSync (mints), Base public RPC receipts (MessageReceived)"},
              open(os.path.join(TRANSFERS, "cctp_mints_provenance.json"), "w"), indent=1)
    print(len(wallets), "candidates,", len(out), "mints")


if __name__ == "__main__":
    main()
