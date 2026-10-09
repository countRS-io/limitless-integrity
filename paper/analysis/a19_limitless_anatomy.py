"""
How the 9Ns5 and AE2J order-book groups traded: daily volume, wallets, markets, prices, fill sizes, and weekly taker fees and rebates.

A wallet belongs to a group because its USDC was bridged in by that group's Solana funder (a06).
Writes paper/out/a19_limitless_anatomy.json and paper/out/a19_*.csv.
Usage: `--groups a:b` processes row groups a to b-1 of the fills file to bound memory, and a run without arguments combines the parts.
"""

import os
from collections import defaultdict

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from analysis.common import (emit, DATA, NORM, OUT, UNLINKED, FLAT, FEE_MODULES, REWARDS, REBATE_WINDOWS, block_time,
                             canon_map, canonical, clusters, fee_usdc, ratio)
from analysis.a11_fee_timeline import usdc_in

NAME = "a19_limitless_anatomy"
COLS = ["exchange", "maker", "taker", "token_id", "maker_side", "shares", "usdc", "fee_raw", "taker_leg", "price",
        "time"]


def week(ts):
    return (ts.dt.tz_convert(None).dt.normalize() - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")


def _new_state():
    return {"daily": defaultdict(float), "wallet": defaultdict(float), "first": {}, "last": {},
            "wallet_week": defaultdict(float), "market": {}, "price": defaultdict(float),
            "size": defaultdict(float), "pairs": defaultdict(float), "fees": defaultdict(float)}


def process_group(i, C, who, cm):
    """Aggregate one row group of the fills file into plain dictionaries."""
    S_ = _new_state()
    daily, wallet, wallet_week, market = S_["daily"], S_["wallet"], S_["wallet_week"], S_["market"]
    price_hist, size_hist, pairs, fees = S_["price"], S_["size"], S_["pairs"], S_["fees"]
    pf = pq.ParquetFile(os.path.join(NORM, "limitless_fills.parquet"))
    f = pf.read_row_group(i, columns=COLS).to_pandas()
    f = f[f.exchange != UNLINKED]
    f["maker"], f["taker"] = f.maker.str.lower(), f.taker.str.lower()
    f["wk"] = week(f.time)

    # Taker fees come from the taker order's own record, whose `maker` is the taker order's signer.
    tl = f[f.taker_leg]
    fee = fee_usdc(tl)
    lab = tl.maker.map(who).fillna("other")
    for (wk, g), v in fee.groupby([tl.wk, lab]).sum().items():
        fees[(wk, g, "taker_fees")] += v
    for wk, v in fee.groupby(tl.wk).sum().items():
        fees[(wk, "venue", "taker_fees")] += v

    f = canonical(f[~f.taker_leg], cm)
    mk, tk = f.maker.map(who), f.taker.map(who)
    f["grp"] = np.where(mk.notna() & (mk == tk), mk.fillna("") + "_inside",
                        np.where(mk.notna(), mk.fillna("") + "_edge",
                                 np.where(tk.notna(), tk.fillna("") + "_edge", "other")))
    f["day"] = f.time.dt.strftime("%Y-%m-%d")
    for (d, g), r in f.groupby(["day", "grp"]).agg(c=("shares", "sum"), u=("usdc", "sum"), n=("shares", "size")).iterrows():
        daily[(d, g, "contracts")] += r.c
        daily[(d, g, "usdc")] += r.u
        daily[(d, g, "fills")] += r.n

    for side in ("maker", "taker"):
        sub = f[f[side].isin(who)]
        if not len(sub):
            continue
        agg = sub.groupby(side).agg(c=("shares", "sum"), u=("usdc", "sum"), n=("shares", "size"),
                                    t0=("time", "min"), t1=("time", "max"))
        for w, r in agg.iterrows():
            wallet[(w, f"contracts_as_{side}")] += r.c
            wallet[(w, f"usdc_as_{side}")] += r.u
            wallet[(w, f"fills_as_{side}")] += r.n
            S_["first"][w] = min(S_["first"].get(w, r.t0), r.t0)
            S_["last"][w] = max(S_["last"].get(w, r.t1), r.t1)
        for (w, wk), v in sub.groupby([side, "wk"]).shares.sum().items():
            wallet_week[(w, wk)] += v

    for k, S in C.items():
        a, b = f.maker.isin(S), f.taker.isin(S)
        ab = a | b
        sub = f[ab]
        if not len(sub):
            continue
        g = pd.DataFrame({"c": sub.condition_id.fillna("?"),
                          "net": sub.maker_delta * a[ab] - sub.maker_delta * b[ab],
                          "gross": sub.shares * (a[ab].astype(int) + b[ab].astype(int)), "t": sub.time})
        for cid, r in g.groupby("c").agg(net=("net", "sum"), gross=("gross", "sum"), t0=("t", "min"), t1=("t", "max")).iterrows():
            market[(k, cid)] = [r.net, r.gross, r.t0, r.t1]

    pb = (f.price.clip(0, 0.9999) * 100).astype(int)
    for (g, b), v in f.groupby([f.grp, pb]).shares.sum().items():
        price_hist[(g, int(b))] += v
    sb = np.floor(np.log10(f.usdc.clip(lower=0.01)) * 4) / 4
    for (g, b), r in f.groupby([f.grp, sb]).agg(n=("shares", "size"), u=("usdc", "sum")).iterrows():
        size_hist[(g, float(b), "fills")] += r.n
        size_hist[(g, float(b), "usdc")] += r.u
    ins = f[f.grp == "9Ns5_inside"]
    for (m_, t_), v in ins.groupby(["maker", "taker"]).shares.sum().items():
        pairs[(m_, t_)] += v
    return {k: (dict(v) if isinstance(v, defaultdict) else v) for k, v in S_.items()}


def merge(parts):
    T = _new_state()
    for P in parts:
        for key in ("daily", "wallet", "wallet_week", "price", "size", "pairs", "fees"):
            for k, v in P[key].items():
                T[key][k] += v
        for w, t in P["first"].items():
            T["first"][w] = min(T["first"].get(w, t), t)
        for w, t in P["last"].items():
            T["last"][w] = max(T["last"].get(w, t), t)
        for k, (n, g, t0, t1) in P["market"].items():
            m = T["market"].setdefault(k, [0.0, 0.0, t0, t1])
            m[0] += n
            m[1] += g
            m[2], m[3] = min(m[2], t0), max(m[3], t1)
    return T


def run(parts):
    C = clusters()
    who = {w: k for k, S in C.items() for w in S}
    T = merge(parts)
    daily, wallet_first, wallet_last = T["daily"], T["first"], T["last"]
    wallet_week, market, price_hist, pairs, fees = (T["wallet_week"], T["market"], T["price"],
                                                    T["pairs"], T["fees"])
    wallet = defaultdict(lambda: defaultdict(float))
    for (w, k), v in T["wallet"].items():
        wallet[w][k] += v
    size_hist = defaultdict(lambda: [0, 0.0])
    for (g, b, k), v in T["size"].items():
        size_hist[(g, b)][0 if k == "fills" else 1] += v

    # Rebates and refunds into cluster wallets, by week.
    lk = usdc_in()[["block", "frm", "to", "usdc"]]
    lk = lk[lk.to.isin(who) & lk.frm.isin({REWARDS, *FEE_MODULES})]
    lk["time"] = block_time(lk.block).tz_localize("UTC")
    lk["wk"] = week(lk.time)
    # Rewards to 9Ns5 over the windows of Limitless's own rebate posts.
    r9 = lk[(lk.to.map(who) == "9Ns5") & (lk.frm == REWARDS)]
    rebate_windows = {k: float(r9[(r9.time >= a) & (r9.time < b)].usdc.sum()) for k, (a, b) in REBATE_WINDOWS.items()}
    lk["who"] = lk.to.map(who)
    lk["kind"] = lk.frm.map({REWARDS: "rewards_received", **{f: "maker_fee_refunds_usdc" for f in FEE_MODULES}})
    for (wk, g, kind), v in lk.groupby(["wk", "who", "kind"]).usdc.sum().items():
        fees[(wk, g, kind)] += v

    d = pd.Series(daily).rename_axis(["day", "group", "field"]).unstack("field").reset_index()
    d.to_csv(os.path.join(OUT, "a19_daily_groups.csv"), index=False)
    W = pd.DataFrame(wallet).T.fillna(0)
    W["cluster"] = W.index.map(who)
    W["first_fill"] = W.index.map(lambda w: wallet_first.get(w))
    W["last_fill"] = W.index.map(lambda w: wallet_last.get(w))
    W.rename_axis("wallet").reset_index().to_csv(os.path.join(OUT, "a19_wallets.csv"), index=False)
    pd.Series(wallet_week).rename_axis(["wallet", "week"]).rename("contracts").reset_index() \
        .to_csv(os.path.join(OUT, "a19_wallet_weekly.csv"), index=False)
    M = pd.DataFrame([(k, c, v[0], v[1], v[2], v[3]) for (k, c), v in market.items()],
                     columns=["cluster", "condition_id", "net", "gross", "first", "last"])
    M.to_csv(os.path.join(OUT, "a19_market_net.csv"), index=False)
    pd.Series(price_hist).rename_axis(["group", "price_cent"]).rename("contracts").reset_index() \
        .to_csv(os.path.join(OUT, "a19_price_hist.csv"), index=False)
    pd.DataFrame([(g, b, v[0], v[1]) for (g, b), v in size_hist.items()],
                 columns=["group", "log10_usdc_bin", "fills", "usdc"]).to_csv(os.path.join(OUT, "a19_size_hist.csv"), index=False)
    F = pd.Series(fees).rename_axis(["week", "who", "kind"]).unstack(["who", "kind"]).fillna(0).sort_index()
    F.columns = [f"{a}_{b}" for a, b in F.columns]
    F.reset_index().to_csv(os.path.join(OUT, "a19_weekly_fees.csv"), index=False)

    # Summary numbers for the text.
    P = pd.Series(pairs)
    res = {}
    for k in C:
        w = W[W.cluster == k]
        both = w[(w.contracts_as_maker > 0) & (w.contracts_as_taker > 0)]
        mm = M[(M.cluster == k) & (M.condition_id != "?")]
        flat = mm.net.abs() < FLAT * mm.gross
        res[k] = {
            "wallets_traded": int(len(w)),
            "wallets_both_maker_and_taker": int(len(both)),
            "maker_share_of_wallet_volume_median": float((w.contracts_as_maker / (w.contracts_as_maker + w.contracts_as_taker)).median()),
            "first_fill": str(w.first_fill.min()), "last_fill": str(w.last_fill.max()),
            "markets": int(len(mm)), "flat_markets_share": float(flat.mean()),
            "net_over_gross": float(mm.net.abs().sum() / mm.gross.sum()),
        }
    first = pd.to_datetime(W[W.cluster == "9Ns5"].first_fill).sort_values()
    res["9Ns5"]["first_60_first_fills"] = [str(first.iloc[0]), str(first.iloc[59])]
    res["9Ns5"]["second_60_first_fills"] = [str(first.iloc[60]), str(first.iloc[-1])]
    res["9Ns5"]["wallets_trading_in_september"] = int((pd.to_datetime(W[W.cluster == "9Ns5"].last_fill) >= "2026-09-01").sum())
    res["AE2J"]["first_fills_by_day"] = pd.to_datetime(W[W.cluster == "AE2J"].first_fill).dt.strftime("%Y-%m-%d").value_counts().sort_index().to_dict()
    for k in C:
        w = W[W.cluster == k]
        ms = w.contracts_as_maker / (w.contracts_as_maker + w.contracts_as_taker)
        res[k]["maker_share_of_wallet_volume_range"] = [float(ms.min()), float(ms.max())]
    # Price band and fill size of 9Ns5's inside trades against everyone else, meaning every other fill, edge fills included.
    ph = pd.Series(price_hist).rename_axis(["group", "cent"])
    sh = pd.DataFrame([(g, v[0], v[1]) for (g, b), v in size_hist.items()], columns=["group", "fills", "usdc"])
    ELSE = ["other", "9Ns5_edge", "AE2J_edge"]
    band = lambda gs: ratio(ph[ph.index.get_level_values(0).isin(gs) & (ph.index.get_level_values(1) >= 10)
                               & (ph.index.get_level_values(1) < 90)].sum(), ph[ph.index.get_level_values(0).isin(gs)].sum())
    fill = lambda gs: ratio(sh[sh.group.isin(gs)].usdc.sum(), sh[sh.group.isin(gs)].fills.sum())
    res["price_10_to_90_cents_share"] = {"9Ns5": band(["9Ns5_inside"]), "everyone_else": band(ELSE)}
    res["average_fill_usdc"] = {"9Ns5": fill(["9Ns5_inside"]), "everyone_else": fill(ELSE)}
    # Taker fees of 9Ns5 against the venue, from the week of its first trade and in May.
    Fw = F.reset_index()
    since = Fw[Fw.week >= "2026-02-16"]
    may = Fw[(Fw.week >= "2026-05-04") & (Fw.week <= "2026-05-25")]
    res["taker_fees"] = {"from_2026-02-16": {"9Ns5": float(since["9Ns5_taker_fees"].sum()), "venue": float(since.venue_taker_fees.sum())},
                         "4_to_31_May": {"9Ns5": float(may["9Ns5_taker_fees"].sum()), "venue": float(may.venue_taker_fees.sum())}}
    res["9Ns5"]["rewards_in_advertised_windows"] = rebate_windows
    res["9Ns5"]["inside_pairs"] = int(len(P))
    res["9Ns5"]["top10_pairs_share_of_inside"] = float(P.nlargest(10).sum() / P.sum()) if len(P) else None
    res["9Ns5"]["top1_pair_share_of_inside"] = float(P.max() / P.sum()) if len(P) else None
    return res


if __name__ == "__main__":
    # A part older than the fills file or the group wallet list is recomputed.
    import pickle, sys
    PARTS = os.path.join(DATA, "tmp_a19")
    os.makedirs(PARTS, exist_ok=True)
    fills = os.path.join(NORM, "limitless_fills.parquet")
    n = pq.ParquetFile(fills).metadata.num_row_groups
    newest_input = max(os.path.getmtime(fills), os.path.getmtime(os.path.join(OUT, "a06_limitless_cluster_wallets.csv")))
    if "--groups" in sys.argv:
        a, b = map(int, sys.argv[sys.argv.index("--groups") + 1].split(":"))
        C = clusters()
        who = {w: k for k, S in C.items() for w in S}
        cm = canon_map()
        for i in range(a, min(b, n)):
            with open(os.path.join(PARTS, f"rg{i:03d}.pkl"), "wb") as fh:
                pickle.dump(process_group(i, C, who, cm), fh)
            print(f"row group {i + 1}/{n}", flush=True)
    else:
        parts = []
        for i in range(n):
            p = os.path.join(PARTS, f"rg{i:03d}.pkl")
            if not os.path.exists(p) or os.path.getmtime(p) < newest_input:
                C = clusters()
                who = {w: k for k, S in C.items() for w in S}
                with open(p, "wb") as fh:
                    pickle.dump(process_group(i, C, who, canon_map()), fh)
            with open(p, "rb") as fh:
                parts.append(pickle.load(fh))
        emit(NAME, run(parts))
