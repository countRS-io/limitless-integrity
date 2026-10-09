"""
One 9Ns5 market, fill by fill: condition 0xa44137...2a61 on 26 May 2026, cited in Section 4 of the paper.

Reads the order-book fills, the token map and the cluster wallets.
Writes paper/out/a19_market_example.csv and .json.
"""

import os

import pandas as pd
import pyarrow.parquet as pq

from analysis.common import NORM, OUT, UNLINKED, canon_map, clusters, emit

CID = "0xa44137590ddc103ef87ce016b325c4ebeccbd986aabb20aba997bfb60f132a61"
LO, HI = pd.Timestamp("2026-05-26", tz="UTC"), pd.Timestamp("2026-05-27", tz="UTC")


def run():
    cm = canon_map()
    toks = set(cm[cm.condition_id.str.lower() == CID].token_id)
    S = clusters()["9Ns5"]

    pf = pq.ParquetFile(os.path.join(NORM, "limitless_fills.parquet"))
    ti = pf.schema_arrow.get_field_index("time")
    cols = ["block", "tx", "exchange", "maker", "taker", "token_id", "maker_side", "shares", "price", "usdc", "taker_leg", "time"]
    parts = []
    for i in range(pf.metadata.num_row_groups):  # Read only the row groups that cover 26 May.
        st = pf.metadata.row_group(i).column(ti).statistics
        mn, mx = pd.Timestamp(st.min), pd.Timestamp(st.max)
        if mn.tzinfo is None:
            mn, mx = mn.tz_localize("UTC"), mx.tz_localize("UTC")
        if mx >= LO and mn < HI:
            f = pf.read_row_group(i, columns=cols).to_pandas()
            f = f[f.token_id.isin(toks) & ~f.taker_leg & (f.exchange != UNLINKED) & (f.time >= LO) & (f.time < HI)]
            if len(f):
                parts.append(f)
    g = pd.concat(parts).sort_values(["time", "block"])
    g["maker"], g["taker"] = g.maker.str.lower(), g.taker.str.lower()
    g["both_9ns5"] = g.maker.isin(S) & g.taker.isin(S)
    g.drop(columns=["taker_leg", "exchange"]).to_csv(os.path.join(OUT, "a19_market_example.csv"), index=False)

    res = {"condition_id": CID, "tokens": {}}
    for tok, h in g.groupby("token_id"):
        w = set(h.maker) | set(h.taker)
        res["tokens"][str(tok)] = {"fills": int(len(h)), "shares": round(float(h.shares.sum()), 3),
                                   "share_inside_9ns5": round(float(h[h.both_9ns5].shares.sum() / h.shares.sum()), 4),
                                   "wallets": len(w), "wallets_9ns5": len(w & S),
                                   "first": str(h.time.min()), "last": str(h.time.max())}
    emit("a19_market_example", res)
    return res


if __name__ == "__main__":
    run()
