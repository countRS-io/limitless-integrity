"""
What the clusters' trading cost them, by month: fees charged, maker-fee refunds and rebates.

Fees come from each OrderFilled log and refunds and rebates from USDC Transfer logs, so cost is measured, not modelled.
Maker fees are refunded in full in the same transaction, partly in outcome tokens that Transfer logs do not show, so they are netted out by rule and the USDC refunds are only a check.
Net cost is taker fees charged minus USDC from the rewards distributor; gas is not counted.

Reads the order-book fills, every USDC transfer into the cluster wallets and the cluster wallets.
Writes paper/out/a11_fee_timeline.json.
"""

import os

import pandas as pd

from analysis.common import emit, NORM, UNLINKED, FEE_MODULES, REWARDS, block_time, clusters, fee_usdc, pulled, ratio

NAME = "a11_fee_timeline"


def usdc_in():
    """Every USDC Transfer into the cluster wallets (py/pull_cluster_usdc_in.py)."""
    d = pulled("cluster_usdc_in_all.parquet")
    d["frm"], d["to"] = d.frm.str.lower(), d.to.str.lower()
    return d


def run():
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"),
                        columns=["time", "exchange", "maker", "taker", "maker_side", "shares", "usdc", "fee_raw",
                                 "taker_leg"])
    f = f[f.exchange != UNLINKED]
    f["fee_usdc"] = fee_usdc(f)
    f["month"] = f.time.dt.strftime("%Y-%m")

    received = usdc_in()
    received["month"] = block_time(received.block).strftime("%Y-%m")

    out = {}
    for name, S in clusters().items():
        mine = f[f.maker.isin(S)]
        charged_maker = mine[~mine.taker_leg].groupby("month").fee_usdc.sum()
        # On a taker-leg record, `maker` is the taker order's signer.
        charged_taker = mine[mine.taker_leg].groupby("month").fee_usdc.sum()
        traded = f[~f.taker_leg & (f.maker.isin(S) | f.taker.isin(S))].groupby("month").usdc.sum()
        got = received[received.to.isin(S)]
        refunds = got[got.frm.isin(FEE_MODULES)].groupby("month").usdc.sum()
        rebates = got[got.frm == REWARDS].groupby("month").usdc.sum()
        m = pd.DataFrame({"traded_usdc": traded, "fees_charged_as_maker": charged_maker,
                          "fees_charged_as_taker": charged_taker, "maker_fee_refunds_usdc_part": refunds,
                          "rebates_and_rewards": rebates}).fillna(0)
        m["net_cost"] = m.fees_charged_as_taker - m.rebates_and_rewards
        t = m.sum()
        out[name] = {"wallets": len(S), "totals": t.round(2).to_dict(),
                     "net_cost_per_100_usdc_traded": ratio(100 * t.net_cost, t.traded_usdc),
                     "rebates_over_taker_fees": ratio(t.rebates_and_rewards, t.fees_charged_as_taker),
                     "monthly": m.round(2).to_dict(orient="index")}
    return out


if __name__ == "__main__":
    emit(NAME, run())
