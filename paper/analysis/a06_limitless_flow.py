"""
The funding chain behind the 9Ns5 cluster, hop by hop, for the flow figure.

Each hop is a set of USDC Transfer logs on Base or CCTP burns and mints between Base and Solana.
Reads the a06 and a11 results, the CCTP mints, the USDC transfers into the cluster wallets and the fee-trail pulls.
Writes paper/out/a06_limitless_flow.json and a06_funding_chain_evidence.csv, which lists every transaction of the first three hops.
"""

import os

import pandas as pd

from analysis.common import (emit, OUT, SAFE, B87F, X7E07, CCTP_BURN, DEP_9NS5, FUNDERS, block_time, clusters, pulled,
                             result, trail)

NAME = "a06_limitless_flow"


def _hop(d):
    return {"transfers": int(len(d)), "usdc": float(d.amount.sum()),
            "first": str(d.time.min())[:10], "last": str(d.time.max())[:10]}


def run():
    # The first three hops: fee recipient to Safe to 0xb87f to the CCTP burn to 9Ns5.
    ev = pd.concat([
        trail("feerec_usdc_out").pipe(lambda d: d[d.to == SAFE]).assign(hop="0x88ea -> Safe 0x7a0b"),
        trail("safe_usdc_out").pipe(lambda d: d[d.to == B87F]).assign(hop="Safe 0x7a0b -> 0xb87f"),
        trail("b87f_usdc_out").pipe(lambda d: d[d.to.isin(CCTP_BURN)]).assign(hop="0xb87f -> CCTP TokenMessengerV2"),
    ], ignore_index=True)
    ev[["block", "time", "tx", "frm", "to", "amount", "hop"]].astype({"block": int}).rename(columns={"amount": "usdc"}) \
        .to_csv(os.path.join(OUT, "a06_funding_chain_evidence.csv"), index=False)
    hops = {h: _hop(g) for h, g in ev.groupby("hop")}

    C = clusters()
    wallets, ae2j = C["9Ns5"], C["AE2J"]
    mints = pulled("cctp_mints.parquet")
    mints = mints[mints.depositor == DEP_9NS5].assign(time=lambda d: block_time(d.block))
    w9 = pd.read_csv(os.path.join(OUT, "a06_limitless_cluster_wallets.csv")).query("cluster == '9Ns5'").sort_values("first_fill")
    first_set = set(w9.wallet.iloc[:len(w9) // 2])
    to9 = mints[mints.recipient.isin(wallets)]
    hops["9Ns5 -> wallets"] = dict(_hop(to9), wallets=len(wallets),
                                   first_set_usdc=float(to9[to9.recipient.isin(first_set)].amount.sum()),
                                   second_set_usdc=float(to9[~to9.recipient.isin(first_set)].amount.sum()))
    to_ae2j = mints[mints.recipient.isin(ae2j)]
    hops["9Ns5 -> AE2J wallets"] = dict(_hop(to_ae2j), wallets=int(to_ae2j.recipient.nunique()))

    # Each wallet's first mint against its own first fill; Base blocks are 2 s apart.
    w = pd.read_csv(os.path.join(OUT, "a06_limitless_cluster_wallets.csv"))
    w = w[w.cluster == "9Ns5"]
    hours = (w.first_mint - w.first_fill) * 2 / 3600
    timing = {"wallets": int(len(hours)), "before_first_fill": int((hours < 0).sum()),
              "within_24h_after": int(((hours >= 0) & (hours < 24)).sum()), "later": int((hours >= 24).sum()),
              "median_hours": float(hours.median()), "max_hours_after": float(hours.max())}

    # Every CCTP burn on Base or Ethereum whose Solana recipient is 9Ns5.
    burns = pulled("fee_trail", "burns_to_9ns5.parquet")
    back = burns[burns.frm.isin(wallets)].assign(time=lambda d: block_time(d.block))
    second = set(w.sort_values("first_fill").wallet.iloc[len(w) // 2:])  # The later half of the wallets.
    hops["wallets -> 9Ns5 (returned)"] = dict(_hop(back), wallets=int(back.frm.nunique()),
                                              wallets_in_second_set=int(back.frm.drop_duplicates().isin(second).sum()))
    hops["0x7e07 -> 9Ns5"] = _hop(burns[burns.frm == X7E07].assign(time=lambda d: block_time(d.block)))
    src = burns.assign(k=burns.frm.where(~burns.frm.isin(wallets), "cluster wallets")).groupby("k").amount.sum()

    b_in, b_out = trail("b87f_usdc_in"), trail("b87f_usdc_out")
    b87f = {"in": float(b_in.amount.sum()), "out": float(b_out.amount.sum()),
            "to_0x7e07": float(b_out[b_out.to == X7E07].amount.sum()),
            "0x7e07_to_9Ns5": float(burns[burns.frm == X7E07].amount.sum()),
            "in_by_sender": b_in.groupby("frm").amount.agg(["count", "sum"]).sort_values("sum", ascending=False)
                                .round(2).rename(columns={"count": "transfers", "sum": "usdc"}).to_dict("index")}

    # USDC into each AE2J wallet before its first fill, by sender.
    w_all = pd.read_csv(os.path.join(OUT, "a06_limitless_cluster_wallets.csv")).set_index("wallet")
    inn = pulled("cluster_usdc_in_all.parquet")
    inn = inn.assign(frm=inn.frm.str.lower(), to=inn.to.str.lower())
    pre = inn[inn.to.isin(ae2j) & (inn.usdc > 0)]
    pre = pre[pre.block < pre.to.map(w_all.first_fill)]
    by = pre.groupby("frm").agg(wallets=("to", "nunique"), usdc=("usdc", "sum"), first_block=("block", "min"))
    by = by[by.wallets >= 2].sort_values("wallets", ascending=False)
    ee7a = "0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055"
    to_groups = inn[inn.frm == ee7a]
    ae2j_before_bridge = {
        "wallets_funded_before_first_fill": int(pre.to.nunique()),
        "by_sender": {k: {"wallets": int(r.wallets), "usdc": round(float(r.usdc), 2),
                          "first": str(block_time([r.first_block])[0])[:10]} for k, r in by.iterrows()},
        "0xee7a_to_AE2J_wallets": {"wallets": int(to_groups[to_groups.to.isin(ae2j)].to.nunique()),
                                   "usdc": round(float(to_groups[to_groups.to.isin(ae2j)].usdc.sum()), 2)},
        "0xee7a_to_9Ns5_wallets": {"wallets": int(to_groups[to_groups.to.isin(wallets)].to.nunique()),
                                   "usdc": round(float(to_groups[to_groups.to.isin(wallets)].usdc.sum()), 2)},
        "0xee7a_to_0xb87f": round(float(b_in[b_in.frm == ee7a].amount.sum()), 2)}

    c = result("a06_limitless_clusters")
    fees = result("a11_fee_timeline")["9Ns5"]
    return {"hops": hops, "b87f": b87f, "into_9Ns5": float(burns.amount.sum()),
            "into_9Ns5_by_sender": src.sort_values(ascending=False).round(2).to_dict(),
            "first_mint_vs_first_fill": timing, "ae2j_before_bridge": ae2j_before_bridge,
            "fees": dict(fees["totals"], net_cost_per_100_usdc_traded=fees["net_cost_per_100_usdc_traded"]),
            "cluster": c["clusters"][FUNDERS[DEP_9NS5]], "venue_contracts": c["contracts"],
            "window": [c["first_fill"][:10], c["last_fill"][:10]]}


if __name__ == "__main__":
    emit(NAME, run())
