"""
Daily AMM volume, split into the wallets DefiLlama excludes as flash-loan wash traders and the rest, and whether the order-book clusters trade on the AMM.

Reads the AMM trades and DefiLlama's flash-loan list.
Writes paper/out/a19_amm_daily.csv and a19_amm_clusters.json.
"""

import os

import pyarrow.parquet as pq

from analysis.common import NORM, OUT, clusters, emit, flashloan_wallets

SIZE = 1e6   # Shares a day; the flash-loan wallets' last day above this is their last day of size.


def run():
    t = pq.read_table(os.path.join(NORM, "limitless_amm_trades.parquet"),
                      columns=["time", "who", "outcome_tokens", "flashloan_listed"]).to_pandas()
    t["day"] = t.time.dt.strftime("%Y-%m-%d")
    t["group"] = t.flashloan_listed.map({True: "amm_flashloan", False: "amm_other"})
    d = t.groupby(["day", "group"]).agg(contracts=("outcome_tokens", "sum")).reset_index()
    d.to_csv(os.path.join(OUT, "a19_amm_daily.csv"), index=False)
    big = d[(d.group == "amm_flashloan") & (d.contracts > SIZE)].iloc[-1]

    # Do the order-book groups ever trade on the AMM, and is any of their wallets on DefiLlama's list?
    who = t.who.str.lower()
    listed = flashloan_wallets()
    res = {"flashloan_list_addresses": len(listed),
           "flashloan_last_day_over_1M_shares": {"day": big.day, "shares": float(big.contracts)}}
    for name, S in clusters().items():
        hit = t[who.isin(S)]
        res[name] = {"wallets": len(S), "amm_trades": int(len(hit)), "amm_wallets": int(hit.who.str.lower().nunique()),
                     "amm_outcome_tokens": float(hit.outcome_tokens.sum()), "on_flashloan_list": len(S & listed)}
    emit("a19_amm_clusters", res)


if __name__ == "__main__":
    run()
