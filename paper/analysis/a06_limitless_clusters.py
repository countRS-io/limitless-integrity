"""
Limitless volume traded between wallets that share one funder: a Solana account that bridged USDC through Circle's CCTP to at least 20 wallets on 10M or more order-book shares.

The funded wallets split into two groups by the calendar year of their first fill, each named after the funder of its earliest mint.
A shared funder says one party paid for the wallets, not who that party is.

Reads the order-book fills and the CCTP mints.
Writes paper/out/a06_limitless_clusters.json and a06_limitless_cluster_wallets.csv.
"""

import json, os

import pandas as pd

from analysis.common import emit, NORM, OUT, TRANSFERS, UNLINKED, FUNDERS, block_time, pulled, ratio

NAME = "a06_limitless_clusters"
MIN_WALLETS = 20


def members(f):
    """One row per funded wallet: its cluster, first fill, first funder mint and USDC bridged by the funders."""
    mints = pulled("cctp_mints.parquet")
    n = mints.groupby("depositor").recipient.nunique()
    m = mints[mints.depositor.isin(n[n >= MIN_WALLETS].index)].sort_values("block")
    first = pd.concat([f.groupby("maker").block.min(), f.groupby("taker").block.min()]).groupby(level=0).min()
    w = m.groupby("recipient").agg(first_mint=("block", "min"), bridged_usdc=("amount", "sum"))
    w["first_fill"] = first.reindex(w.index)
    w["wave"] = block_time(w.first_fill).year.values
    earliest = m.assign(wave=m.recipient.map(w.wave)).groupby("wave").depositor.first()
    w["cluster"] = w.wave.map(earliest).map(lambda d: FUNDERS[d][:4])
    return w.rename_axis("wallet").reset_index()[["wallet", "cluster", "first_fill", "first_mint", "bridged_usdc"]]


def funding(w):
    """The rule's inputs, and each funder's mints into each cluster."""
    with open(os.path.join(TRANSFERS, "cctp_mints_provenance.json")) as fh:
        prov = json.load(fh)
    mints = pulled("cctp_mints.parquet")
    n = mints.groupby("depositor").recipient.nunique()
    m = mints[mints.depositor.isin(n[n >= MIN_WALLETS].index)].merge(w[["wallet", "cluster"]], left_on="recipient", right_on="wallet")
    m["time"] = block_time(m.block).values
    by = {}
    for (d, c), g in m.groupby(["depositor", "cluster"]):
        by[f"{FUNDERS[d][:4]} -> {c} wallets"] = {
            "transfers": int(len(g)), "usdc": float(g.amount.sum()), "wallets": int(g.recipient.nunique()),
            "first": str(g.time.min())[:10], "last": str(g.time.max())[:10],
            "submitted_by_recipient": int((g.sender == g.recipient).sum())}
    return {"candidates": prov["candidates"], "min_contracts": prov["min_contracts"], "min_wallets": MIN_WALLETS,
            "funders": int((n >= MIN_WALLETS).sum()), "funded_wallets": int(len(w)),
            "depositors": int(len(n)), "by_funder": by}


def run():
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"),
                        columns=["block", "time", "maker", "taker", "shares", "usdc", "taker_leg", "exchange"])
    f = f[~f.taker_leg & (f.exchange != UNLINKED)]
    w = members(f)
    w.to_csv(os.path.join(OUT, "a06_limitless_cluster_wallets.csv"), index=False)
    full = {v[:4]: v for v in FUNDERS.values()}
    clusters = {full[c]: set(g.wallet) for c, g in w.groupby("cluster")}
    bridged = w.groupby("cluster").bridged_usdc.sum()
    total = f.shares.sum()
    out = {}
    for name, S in clusters.items():
        inside = f.maker.isin(S) & f.taker.isin(S)
        touch = f.maker.isin(S) | f.taker.isin(S)
        out[name] = {
            "wallets": len(S),
            "bridged_usdc": float(bridged[name[:4]]),
            "inside_contracts": float(f[inside].shares.sum()),
            "inside_usdc": float(f[inside].usdc.sum()),
            "inside_share": float(f[inside].shares.sum() / total),
            "touch_share": float(f[touch].shares.sum() / total),
        }
    a, b = clusters.values()
    cross = (f.maker.isin(a) & f.taker.isin(b)) | (f.maker.isin(b) & f.taker.isin(a))
    within = f.maker.isin(a | b) & f.taker.isin(a | b)
    touch = f.maker.isin(a | b) | f.taker.isin(a | b)
    between = {"contracts": float(f[cross].shares.sum()),
               "share_of_fills_within_both_groups": ratio(f[cross].shares.sum(), f[within].shares.sum()),
               "share_of_fills_touching_either_group": ratio(f[cross].shares.sum(), f[touch].shares.sum())}
    return {"clusters": out, "funding": funding(w), "between_clusters": between, "fills": int(len(f)), "contracts": float(total),
            "first_fill": str(f.time.min()), "last_fill": str(f.time.max())}


if __name__ == "__main__":
    emit(NAME, run())
