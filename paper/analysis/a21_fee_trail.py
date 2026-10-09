"""
Where the taker fees the two order-book groups paid went, and each group's USDC ledger.

Writes paper/out/a21_fee_trail.json.
"""

import os
from collections import deque

import numpy as np
import pandas as pd

from analysis.common import (emit, NORM, BASE_GENESIS, UNLINKED, CTF, EXCHANGES, FEE_MODULES, REWARDS, CCTP_BURN,
                             DEP_9NS5, REBATE_WINDOWS, clusters, fee_usdc, pulled, ratio, trail)
from analysis.a11_fee_timeline import usdc_in

NAME = "a21_fee_trail"
ZERO = "0x" + "0" * 40


def walk(ins, outs, fifo=False):
    """
    Carry a tagged share through one address.

    `ins` and `outs` have block, log_index and amount, and `ins` also has the tagged fraction `f`.
    Returns `outs` with the tagged amount each outflow carried, and the balance and tagged balance left.
    Pro rata: every outflow carries the address's tagged share at that moment. FIFO: outflows draw on the inflows in the order they arrived.
    """
    ev = pd.concat([ins.assign(d=1), outs.assign(d=-1, f=0.0)], ignore_index=True)
    ev = ev.sort_values(["block", "log_index", "d"], ascending=[True, True, False])
    bal = tag = 0.0
    queue, carried = deque(), {}
    for i, d, amount, f in zip(ev.index, ev.d.values, ev.amount.values, ev.f.values):
        if d > 0:
            bal += amount
            tag += amount * f
            queue.append([amount, f])
            continue
        if fifo:
            need, t = amount, 0.0
            while need > 1e-9 and queue:
                take = min(need, queue[0][0])
                t += take * queue[0][1]
                queue[0][0] -= take
                need -= take
                if queue[0][0] <= 1e-9:
                    queue.popleft()
        else:
            t = amount * (tag / bal) if bal > 0 else 0.0
        t = min(t, tag)
        carried[i] = t
        bal -= amount
        tag -= t
    out = ev[ev.d < 0].assign(tagged=lambda x: x.index.map(carried)).drop(columns=["d", "f"])
    return out, {"balance_left": bal, "tagged_left": tag}


def fees_by_block():
    """Taker fees charged on the order book, in USDC, by block: all traders, 9Ns5 and AE2J."""
    f = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"),
                        columns=["block", "exchange", "maker", "maker_side", "shares", "usdc", "fee_raw", "taker_leg"])
    f = f[f.taker_leg & (f.exchange != UNLINKED) & (f.fee_raw > 0)]
    f = f.assign(fee=fee_usdc(f))
    C = clusters()
    out = f.groupby("block").fee.sum().rename("all").to_frame()
    for n, S in C.items():
        out[n] = f[f.maker.isin(S)].groupby("block").fee.sum()
    return out.fillna(0).sort_index()


def tag_fee_inflows(ins, fb, who):
    """Tag each fee-derived inflow with the share of its week's taker fees (Monday to Sunday, UTC) paid by the groups in `who`."""
    wk = lambda blocks: ((BASE_GENESIS + 2 * np.asarray(blocks)) // 86400 + 3) // 7   # Day 0, 1 Jan 1970, was a Thursday.
    w = fb.groupby(wk(fb.index.values)).sum()
    share = (sum(w[c] for c in who) / w["all"]).fillna(0.0)
    return ins.assign(f=pd.Series(wk(ins.block.values)).map(share).fillna(0.0).values)


def ledger(S, inn, out, allS):
    """USDC into and out of a set of wallets, by counterparty."""
    def cat(a):
        if a in EXCHANGES: return "exchanges"
        if a == CTF: return "conditional_tokens"
        if a in FEE_MODULES: return "fee_modules"
        if a == REWARDS: return "rewards_distributor"
        if a == ZERO: return "cctp_mints"
        if a in CCTP_BURN: return "cctp_burns"
        if a in S: return "own_wallets"
        if a in allS: return "other_cluster"
        return "anyone_else"
    i = inn[inn.to.isin(S)]
    o = out[out.frm.isin(S)]
    i_c = i.groupby(i.frm.map(cat)).usdc.sum()
    o_c = o.groupby(o.to.map(cat)).usdc.sum()
    return {"in": i_c.round(2).to_dict(), "out": o_c.round(2).to_dict(),
            "in_total": float(i.usdc.sum()), "out_total": float(o.usdc.sum()),
            "left_in_wallets": float(i.usdc.sum() - o.usdc.sum()),
            "anyone_else_out_top": o[o.to.map(cat) == "anyone_else"].groupby("to").usdc.sum().nlargest(10).round(2).to_dict()}


def chain(fb, who, fifo=False):
    """Follow the tagged fees from the fee recipient to the Safe, 0xb87f, 0x7e07, 9Ns5 and the wallets."""
    rin = trail("feerec_usdc_in")
    # Fee income is the fee modules' USDC and the USDC the fee recipient redeems from the conditional-tokens contract for outcome tokens taken as fees.
    fee_like = rin.frm.isin(FEE_MODULES) | (rin.frm == CTF)
    tagged_in = tag_fee_inflows(rin[fee_like], fb, who)
    rec_ins = pd.concat([tagged_in, rin[~fee_like].assign(f=0.0)], ignore_index=True)
    rec_out = trail("feerec_usdc_out")
    rec_o, rec_left = walk(rec_ins, rec_out, fifo)

    def from_outs(ins, *sources):
        """Tag the inflows of the next address with what the matching outflow of each source carried."""
        m = {}
        for o in sources:
            m.update(((t, i), g / a) for t, i, g, a in zip(o.tx, o.log_index, o.tagged, o.amount))
        return ins.assign(f=[m.get((t, i), 0.0) for t, i in zip(ins.tx, ins.log_index)])

    s_in = from_outs(trail("safe_usdc_in"), rec_o)
    s_o, s_left = walk(s_in, trail("safe_usdc_out"), fifo)

    b_in = from_outs(trail("b87f_usdc_in"), s_o)
    b_out = trail("b87f_usdc_out")
    b_o, b_left = walk(b_in, b_out, fifo)

    x_in = from_outs(trail("x7e07_usdc_in"), b_o)
    x_o, x_left = walk(x_in, trail("x7e07_usdc_out"), fifo)

    # The rebate loop: fee recipient and Safe to 0x6661, 0x6661 to the rewards distributor, rebates out.
    six_o, six_left = walk(from_outs(trail("x6661_usdc_in"), rec_o, s_o), trail("x6661_usdc_out"), fifo)
    rw_o, rw_left = walk(from_outs(trail("rewards_usdc_in"), six_o), trail("rewards_usdc_out"), fifo)
    C = clusters()
    rebate_loop = {"x6661_out_tagged_by_destination": six_o.groupby("to").tagged.sum().nlargest(6).round(2).to_dict(),
                   "x6661": six_left, "rewards_distributor": rw_left,
                   "rebates_tagged_to": {n: float(rw_o[rw_o.to.isin(S)].tagged.sum()) for n, S in C.items()},
                   "rebates_to": {n: float(rw_o[rw_o.to.isin(S)].amount.sum()) for n, S in C.items()},
                   "rebates_tagged_to_anyone_else": float(rw_o[~rw_o.to.isin(set().union(*C.values()))].tagged.sum())}

    # 9Ns5's inflows are the CCTP burns to it; each burn carries what the sender's USDC transfer into the burn contract in the same transaction carried.
    # The two Ethereum burns carry nothing and have Ethereum block numbers, which cannot be ordered against Base blocks, so they are left out.
    burn_tag = {t: g / a for o in (b_o, x_o) for t, g, a, to in zip(o.tx, o.tagged, o.amount, o.to) if to in CCTP_BURN}
    sol = trail("burns_to_9ns5")
    sol = sol[sol.chain == "Base"]
    sol["f"] = sol.tx.map(burn_tag).fillna(0.0)
    mints = pulled("cctp_mints.parquet")
    mints = mints[mints.depositor == DEP_9NS5].assign(log_index=0)
    n_o, n_left = walk(sol[["block", "log_index", "amount", "f", "frm"]], mints[["block", "log_index", "amount", "recipient", "tx"]], fifo)
    back_rebates = sum(rebate_loop["rebates_tagged_to"].values())
    back_funding = float(n_o[n_o.recipient.isin(set().union(*C.values()))].tagged.sum())
    tagged_total = float((tagged_in.amount * tagged_in.f).sum())
    charged = float(sum(fb[c].sum() for c in who))
    return {
        "came_back": {"as_rebates": back_rebates, "as_funding": back_funding, "total": back_rebates + back_funding,
                      "share_of_fees_reaching_fee_recipient": ratio(back_rebates + back_funding, tagged_total),
                      "share_of_fees_charged": ratio(back_rebates + back_funding, charged)},
        "rebate_loop": rebate_loop,
        "fee_recipient": {"fee_inflows": float(tagged_in.amount.sum()), "tagged_in": tagged_total,
                          "other_inflows": float(rin[~fee_like].amount.sum()),
                          "out_tagged_by_destination": rec_o.groupby("to").tagged.sum().nlargest(12).round(2).to_dict(),
                          "out_by_destination": rec_o.groupby("to").amount.sum().nlargest(12).round(2).to_dict(), **rec_left},
        "safe": {"out_tagged_by_destination": s_o.groupby("to").tagged.sum().nlargest(10).round(2).to_dict(),
                 "out_by_destination": s_o.groupby("to").amount.sum().nlargest(10).round(2).to_dict(), **s_left},
        "b87f": {"out_tagged_by_destination": b_o.groupby("to").tagged.sum().round(2).to_dict(), **b_left},
        "x7e07": {"in_by_source": x_in.groupby("frm").amount.sum().nlargest(8).round(2).to_dict(),
                  "out_tagged_by_destination": x_o.groupby("to").tagged.sum().nlargest(8).round(2).to_dict(), **x_left},
        "9Ns5": {"in_tagged_by_sender": sol.assign(t=sol.amount * sol.f).groupby("frm").t.sum().nlargest(5).round(2).to_dict(),
                 "to_9Ns5_wallets_tagged": float(n_o[n_o.recipient.isin(C["9Ns5"])].tagged.sum()),
                 "to_AE2J_wallets_tagged": float(n_o[n_o.recipient.isin(C["AE2J"])].tagged.sum()), **n_left},
    }


def run():
    C = clusters()
    allS = set().union(*C.values())
    inn = usdc_in()
    out = trail("cluster_usdc_out").rename(columns={"amount": "usdc"})
    out["frm"], out["to"] = out.frm.str.lower(), out.to.str.lower()
    fb = fees_by_block()
    rw = trail("rewards_usdc_in")
    rw_out = trail("rewards_usdc_out")
    res = {
        "taker_fees": {"all": float(fb["all"].sum()), **{n: float(fb[n].sum()) for n in C}},
        "ledger": {n: ledger(S, inn, out, allS) for n, S in C.items()},
        "rewards_distributor": {"in_by_source": rw.groupby("frm").amount.sum().nlargest(10).round(2).to_dict(),
                                "out_total": float(rw_out.amount.sum()),
                                # Paid to everyone over the windows of Limitless's two rebate posts (a19).
                                "out_in_advertised_windows": {k: float(rw_out[(rw_out.time >= a) & (rw_out.time < b)].amount.sum())
                                                              for k, (a, b) in REBATE_WINDOWS.items()}},
        "trail_pro_rata": chain(fb, ["9Ns5", "AE2J"]),
        "trail_fifo": chain(fb, ["9Ns5", "AE2J"], fifo=True),
    }
    return res


if __name__ == "__main__":
    emit(NAME, run())
