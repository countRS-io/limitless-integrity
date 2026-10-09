"""
Weekly Limitless notional across both venues, split by who traded it, for the figure.

The parts are order-book trades inside 9Ns5, inside AE2J and the rest, and AMM trades by DefiLlama's flash-loan wallets and the rest.
Reads the a17 inputs, the cluster wallets and paper/out/a17_limitless_claims.csv.
Writes paper/out/a17_limitless_weekly.csv and .json.
"""

import os

import pandas as pd

from analysis.common import NORM, OUT, UNLINKED, clusters, emit, ratio
from analysis.a17_limitless_claims import _tape


def run():
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"),
                        columns=["maker", "taker", "taker_leg", "exchange"])
    f = f[~f.taker_leg & (f.exchange != UNLINKED)]
    t = _tape()  # Order-book rows come first, in the same order as f.
    part = pd.Series("orderbook_other", index=t.index)
    ob = t.index[t.venue == "orderbook"]
    for name, S in clusters().items():
        inside = (f.maker.isin(S) & f.taker.isin(S)).values
        part.loc[ob[inside]] = "orderbook_" + name
    amm = t.venue == "amm"
    part[amm] = "amm_other"
    part[amm & t.flashloan] = "amm_flashloan"
    t["part"] = part
    t["week"] = (t.time.dt.normalize() - pd.to_timedelta(t.time.dt.weekday, unit="D")).dt.tz_localize(None)
    w = t.pivot_table(index="week", columns="part", values="notional", aggfunc="sum", fill_value=0)
    w.to_csv(os.path.join(OUT, "a17_limitless_weekly.csv"))

    # Each dated claim's window, split into the three groups and everyone else.
    t["group"] = t.part.isin(["amm_flashloan"] + ["orderbook_" + n for n in clusters()])
    claims = pd.read_csv(os.path.join(OUT, "a17_limitless_claims.csv"))
    split = {}
    for c in claims[claims.kind.isin(["window", "cumulative"])].itertuples():
        x = t[(t.time < pd.Timestamp(c.end, tz="UTC")) & ((t.time >= pd.Timestamp(c.start, tz="UTC")) if c.kind == "window" else True)]
        split[c.id] = {"onchain": float(x.notional.sum()), "groups": float(x[x.group].notional.sum()),
                       "else": float(x[~x.group].notional.sum()), "onchain_usd": float(x.usd.sum()),
                       "groups_usd": float(x[x.group].usd.sum()), "else_usd": float(x[~x.group].usd.sum())}

    def share(a, b):
        x = t[(t.time >= pd.Timestamp(a, tz="UTC")) & (t.time < pd.Timestamp(b, tz="UTC"))]
        return {"shares": ratio(x[x.group].notional.sum(), x.notional.sum()),
                "usd": ratio(x[x.group].usd.sum(), x.usd.sum())}
    flash = t[t.part == "amm_flashloan"]
    else_monthly = t[~t.group].groupby(t.time.dt.strftime("%Y-%m")).notional.sum()
    return {"claims": split, "else_monthly": else_monthly.round(0).to_dict(),
            "total": float(t.notional.sum()), "else_total": float(t[~t.group].notional.sum()),
            "total_usd": float(t.usd.sum()), "else_total_usd": float(t[~t.group].usd.sum()),
            "groups_share": {"16_Feb_to_30_Jun": share("2026-02-16", "2026-07-01"),
                             "Jul_to_Sep": share("2026-07-01", "2026-10-01"),
                             "Sep": share("2026-09-01", "2026-10-01"),
                             "full_history": share("2024-01-01", "2026-10-01")},
            "first_19_days_of_April": float(t[(t.time >= pd.Timestamp("2026-04-01", tz="UTC"))
                                              & (t.time < pd.Timestamp("2026-04-20", tz="UTC"))].notional.sum()),
            "flashloan_first_trade": str(flash.time.min()),
            "flashloan_usd_per_share": ratio(flash.usd.sum(), flash.notional.sum()),
            "flashloan_before_1_April": float(flash[flash.time < pd.Timestamp("2026-04-01", tz="UTC")].notional.sum()),
            "by_part": w.sum().round(0).to_dict()}


if __name__ == "__main__":
    emit("a17_limitless_weekly", run())
