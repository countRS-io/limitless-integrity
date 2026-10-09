"""
How much Limitless order-book volume has the same address, or the same funder cluster, on both sides.

Also measures whether each cluster, treated as one trader, ends flat in the markets it trades, against the highest-volume wallets outside the clusters.
Reads the order-book fills, the token map and the cluster wallets.
Writes paper/out/a08_self_crossing.json.
"""

import os

import pandas as pd

from analysis.common import emit, clusters, canon_map, canonical, ratio, NORM, UNLINKED, FLAT

NAME = "a08_self_crossing"


def group_stats(f, S):
    """Share of all volume with a group member on both sides, and on at least one side."""
    mk, tk = f.maker.isin(S), f.taker.isin(S)
    total = f.shares.sum()
    inside, touch = f[mk & tk].shares.sum(), f[mk | tk].shares.sum()
    return {"inside_share": float(inside / total), "touch_share": float(touch / total),
            "internal_share_of_group_volume": ratio(inside, touch)}


def top_group(f, n, exclude=()):
    vol = pd.concat([f[["maker", "shares"]].rename(columns={"maker": "a"}),
                     f[["taker", "shares"]].rename(columns={"taker": "a"})]).groupby("a").shares.sum()
    return set(vol.drop(list(set(exclude) & set(vol.index))).nlargest(n).index)


def self_share(f):
    return float(f[f.maker == f.taker].shares.sum() / f.shares.sum())


def cluster_flat(f, S):
    """Treat the cluster as one trader: net position per market against gross traded, where inside fills move no net position and count twice in gross."""
    mk, tk = f.maker.isin(S), f.taker.isin(S)
    net = (f.maker_delta * mk - f.maker_delta * tk).groupby(f.condition_id).sum()
    gross = (f.shares * (mk.astype(int) + tk.astype(int))).groupby(f.condition_id).sum()
    gross = gross[gross > 0]
    flat = net.reindex(gross.index).abs() < FLAT * gross
    once = (f.shares * (mk | tk)).groupby(f.condition_id).sum().reindex(gross.index)
    flat_once = net.reindex(gross.index).abs() < FLAT * once
    return {"markets": int(len(gross)), "flat_markets_share": float(flat.mean()),
            "net_over_gross": float(net.abs().sum() / gross.sum()),
            "counted_once": {"flat_markets_share": float(flat_once.mean()),
                             "net_over_gross": float(net.abs().sum() / once.sum())}}


def wallet_flat(f, S):
    """Each wallet on its own: net position per market against what it traded there."""
    m = f[f.maker.isin(S)][["maker", "condition_id", "maker_delta", "shares"]].rename(columns={"maker": "w"})
    t = f[f.taker.isin(S)][["taker", "condition_id", "maker_delta", "shares"]].rename(columns={"taker": "w"})
    t["maker_delta"] = -t.maker_delta
    p = pd.concat([m, t]).groupby(["w", "condition_id"]).agg(net=("maker_delta", "sum"), gross=("shares", "sum"))
    flat = p.net.abs() < FLAT * p.gross
    return {"positions": int(len(p)), "flat_share": float(flat.mean()),
            "flat_share_by_volume": float(p.gross[flat].sum() / p.gross.sum()),
            "net_over_gross": float(p.net.abs().sum() / p.gross.sum())}


def run():
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"))
    f = f[~f.taker_leg & (f.exchange != UNLINKED)]
    f = canonical(f, canon_map())
    C = clusters()
    out = {"limitless": {"contracts": float(f.shares.sum()), "self_share": self_share(f)}}
    for name, S in C.items():
        g = group_stats(f, S)
        g["wallets"] = len(S)
        g["flat"] = cluster_flat(f, S)
        g["per_wallet"] = wallet_flat(f, S)
        out[name] = g
    cl = C["9Ns5"] | C["AE2J"]
    top = top_group(f, len(C["9Ns5"]), cl)  # As many wallets as 9Ns5 has.
    out["limitless_top120_excl_clusters"] = dict(group_stats(f, top), wallets=len(top), flat=cluster_flat(f, top),
                                                 per_wallet=wallet_flat(f, top))

    return out


if __name__ == "__main__":
    emit(NAME, run())
