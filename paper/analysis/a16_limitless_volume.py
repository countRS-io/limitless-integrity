"""
Limitless order-book volume day by day, and how much of it is concentrated, self-crossed, reciprocal or left no net position.

Exchange 0x71aceb0c is reported apart: nothing on chain ties it to the six linked exchanges.
Reads the order-book fills and the token map.
Writes paper/out/a16_limitless_volume.json and a16_limitless_daily.csv.
"""

import os

import numpy as np
import pandas as pd

from analysis.common import emit, NORM, OUT, UNLINKED, FLAT, canon_map, canonical

NAME = "a16_limitless_volume"


def _daily(f):
    f = f.assign(day=f.time.dt.floor("D"))
    g = f.groupby("day")
    d = pd.DataFrame({
        "fills": g.size(),
        "contracts": g.shares.sum(),
        "usdc": g.usdc.sum(),
        "fee_fill_share": g.fee_raw.apply(lambda s: (s > 0).mean()),
    })
    both = pd.concat([f[["day", "maker", "shares"]].rename(columns={"maker": "addr"}),
                      f[["day", "taker", "shares"]].rename(columns={"taker": "addr"})])
    per = both.groupby(["day", "addr"]).shares.sum()
    d["addresses"] = per.groupby(level=0).size()
    d["top10_share"] = per.groupby(level=0).apply(lambda s: s.nlargest(10).sum() / s.sum())

    d["self_share"] = f[f.maker == f.taker].groupby("day").shares.sum() / d.contracts

    # Reciprocal: volume between two addresses that each took the other's order that day.
    directed = set(zip(f.day, f.maker, f.taker))
    recip = [(dy, t, m) in directed and m != t for dy, m, t in zip(f.day, f.maker, f.taker)]
    d["reciprocal_share"] = f[recip].groupby("day").shares.sum() / d.contracts

    pos = pd.concat([f[["condition_id", "maker", "maker_delta", "shares"]]
                     .rename(columns={"maker": "addr", "maker_delta": "delta"}),
                     f[["condition_id", "taker", "maker_delta", "shares"]]
                     .rename(columns={"taker": "addr"}).assign(delta=lambda x: -x.maker_delta)
                     .drop(columns="maker_delta")])
    book = pos.groupby(["condition_id", "addr"]).agg(net=("delta", "sum"), gross=("shares", "sum"))
    flat = set(book[(book.net.abs() < FLAT * book.gross)].index)
    fm = [(c, a) in flat for c, a in zip(f.condition_id, f.maker)]
    ft = [(c, a) in flat for c, a in zip(f.condition_id, f.taker)]
    # A fill counts half for each flat side, so a fill between two flat books counts in full.
    f = f.assign(flat_w=(np.array(fm, float) + np.array(ft, float)) / 2)
    d["flat_share"] = (f.flat_w * f.shares).groupby(f.day).sum() / d.contracts
    return d.fillna(0)


def run():
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"))
    f = canonical(f[~f.taker_leg], canon_map())
    linked, unlinked = f[f.exchange != UNLINKED], f[f.exchange == UNLINKED]
    daily = _daily(linked)
    daily.to_csv(os.path.join(OUT, "a16_limitless_daily.csv"))
    m = linked.set_index("time").resample("MS")
    monthly = pd.DataFrame({"contracts": m.shares.sum(), "usdc": m.usdc.sum(), "fills": m.size()})
    return {
        "maker_fills": int(len(linked)),
        "first_fill": str(linked.time.min()), "last_fill": str(linked.time.max()),
        "contracts": float(linked.shares.sum()), "usdc": float(linked.usdc.sum()),
        "unmapped_token_share": float(linked.condition_id.isna().mean()),
        "by_exchange": linked.groupby("exchange").agg(fills=("shares", "size"),
                                                      contracts=("shares", "sum"),
                                                      first=("time", "min"), last=("time", "max"))
                             .astype(str).to_dict("index"),
        "monthly": monthly.round(2).astype({"fills": int}).rename(index=lambda t: t.strftime("%Y-%m"))
                          .to_dict("index"),
        "unlinked_exchange": {"fills": int(len(unlinked)), "contracts": float(unlinked.shares.sum())},
        "flat_threshold": FLAT,
    }


if __name__ == "__main__":
    emit(NAME, run())
