"""
The funding chain from Limitless's fee recipient to the 9Ns5 wallets, drawn as a figure.

Reads the a06, a08 and a19 results and the Safe owner snapshots in refs/sources/safe_owners.json.
"""

import json, math, os, textwrap
import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import FancyBboxPatch

from analysis.style import (INK, INK_2, BLUE, REBATE, RETURN, TEXT, span, money, new_fig, head, layout,
                            footer, save)
from analysis.common import SAFE, SOURCES, result


def joined(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def safe_peers():
    """Owner count and threshold of the Safe 0x7a0b, and the labelled multisigs with the same owners and threshold at every snapshot."""
    with open(os.path.join(SOURCES, "safe_owners.json")) as fh:
        s = json.load(fh)["safes"]
    snap = lambda v: [(sorted(v[k]["owners"]), v[k]["threshold"]) for k in ("first_transfer", "last_transfer", "end_of_window")]
    mine = snap(s[SAFE])
    peers = sorted(v["label"].split(" (")[0].replace(" Multisig", "").replace(" Wallet", "")
                   for a, v in s.items() if a != SAFE and snap(v) == mine)
    return len(mine[0][0]), mine[0][1], peers


def flow():
    """The funding chain from Limitless's fee recipient to the 9Ns5 wallets, and back."""
    d = result("a06_limitless_flow")
    h, c, fee, tm = d["hops"], d["cluster"], d["fees"], d["first_mint_vs_first_fill"]
    a8 = result("a08_self_crossing")["9Ns5"]
    a19 = result("a19_limitless_anatomy")["9Ns5"]
    n_own, thr, peers = safe_peers()
    per = lambda k: span(h[k]["first"], h[k]["last"])

    fig = new_fig(7.8)
    ax = fig.add_axes([0.01, 0.21, 0.98, 0.63])
    ax.set_xlim(0, 100); ax.set_ylim(-1.5, 105); ax.axis("off")

    def box(x, y, w, hgt, title, body, col=INK_2, fill="#f1f0ec"):
        ax.add_patch(FancyBboxPatch((x, y), w, hgt, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fill, ec=col, lw=1.0))
        ax.annotate(title, (x + w / 2, y + hgt), xytext=(0, -6), textcoords="offset points", ha="center", va="top",
                    fontsize=TEXT + 0.5, fontweight="bold", color=INK)
        ax.annotate(body, (x + w / 2, y + hgt), xytext=(0, -21), textcoords="offset points", ha="center", va="top",
                    fontsize=TEXT, color=INK_2, linespacing=1.35)

    def arrow(x0, y0, x1, y1, col=INK_2, rad=0.0):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3, shrinkA=2, shrinkB=2,
                                    connectionstyle=f"arc3,rad={rad}"))

    def label(x, y, text, col=INK_2, ha="center", va="bottom"):
        ax.text(x, y, text, ha=ha, va=va, fontsize=TEXT, color=col, linespacing=1.3)

    W, X = 27, (1, 36.5, 72)
    gap = lambda i: (X[i] + W + X[i + 1]) / 2
    y1, y2, hb = 78, 40, 23
    blue_fill = "#e8f0fb"

    box(X[0], y1, W, hb, "Fee recipient", "Limitless, 0x88ea…87b1;\nnamed FEE_RECIPIENT in\nDefiLlama's adapter; receives\nthe fee modules' USDC")
    box(X[1], y1, W, hb, "Safe multisig", f"0x7a0b…ac4c, {thr}-of-{n_own};\n" +
        textwrap.fill(f"same {n_own} owners as the {joined(peers)} multisigs on Limitless's token page", 25))
    box(X[2], y1, W, hb, "Base wallet", f"0xb87f…ed33\npass-through:\n{money(d['b87f']['in'])} in, {money(d['b87f']['out'])} out")
    box(X[2], y2, W, hb, "Solana account", f"9Ns5…Nzuw\nreceived {money(d['into_9Ns5'])},\nall through Circle CCTP", col=BLUE)
    box(X[1], y2, W, hb, f"{tm['wallets']} Base wallets",
        f"{tm['before_first_fill']} of {tm['wallets']} funded before their\nfirst trade, the rest within "
        f"{math.ceil(tm['max_hours_after'])} h;\nmints submitted by the\nwallets themselves", col=BLUE, fill=blue_fill)
    box(X[0], y2, W, hb, "Rewards distributor", "Limitless, 0xE895…FaDB;\nnamed in DefiLlama's adapter;\npays maker rebates")

    k1, k2, k3, k4 = "0x88ea -> Safe 0x7a0b", "Safe 0x7a0b -> 0xb87f", "0xb87f -> CCTP TokenMessengerV2", "9Ns5 -> wallets"
    mid1, mid2 = y1 + hb / 2, y2 + hb * 0.62
    for i, k in ((0, k1), (1, k2)):
        arrow(X[i] + W + 1, mid1, X[i + 1] - 1, mid1)
        label(gap(i), y1 + hb + 1.5, f"{h[k]['transfers']} transfers\n{money(h[k]['usdc'])}\n{per(k)}")
    cx = X[2] + 7
    arrow(cx, y1 - 1, cx, y2 + hb + 1)
    when = span(h[k3]["first"], h[k3]["last"]).replace(" to ", " to\n")
    label(cx + 2, (y1 + y2 + hb) / 2, f"{h[k3]['transfers']} bridge transfers\n{money(h[k3]['usdc'])}\n{when}",
          ha="left", va="center")
    arrow(X[2] - 1, mid2, X[1] + W + 1, mid2, col=BLUE)
    label(gap(1), y2 + hb + 1.5, f"{h[k4]['transfers']:,} bridge transfers\n{money(h[k4]['usdc'])}\n{per(k4)}", col=BLUE)
    arrow(X[0] + W + 1, mid2, X[1] - 1, mid2, col=REBATE)
    label(gap(0), y2 + hb + 1.5, f"rebates\n{money(fee['rebates_and_rewards'])}", col=REBATE)
    k5 = "wallets -> 9Ns5 (returned)"
    arrow(X[1] + W + 1, y2 + 5, X[2] - 1, y2 + 5, col=RETURN, rad=0.45)
    label(gap(1), y2 - 2, f"{h[k5]['wallets']} wallets send\n{money(h[k5]['usdc'])} back\n"
          f"{span(h[k5]['first'], h[k5]['last'], False)}", col=RETURN, va="top")

    win = span(a19["first_fill"][:10], a19["last_fill"][:10])
    box(36, 0, 63, 21, f"The {c['wallets']} wallets trade with each other",
        f"{c['inside_share']:.0%} of all Limitless order-book volume has one of these wallets\non both sides: "
        f"{c['inside_contracts'] / 1e9:.2f}B shares, {money(c['inside_usdc'])} traded ({win}).\n"
        f"{a8['internal_share_of_group_volume']:.1%} of their volume is with each other; as one trader\n"
        f"they end flat in {a8['flat']['flat_markets_share']:.0%} of the {a8['flat']['markets']:,} markets they traded",
        col=BLUE, fill=blue_fill)
    arrow(X[1] + 5, y2 - 1, X[1] + 5, 21 + 1, col=BLUE)
    box(1, 0, 31, 21, "What the trading cost them",
        f"taker fees paid: {money(fee['fees_charged_as_taker'])}\n"
        f"rebates from 0xE895…FaDB: {money(fee['rebates_and_rewards'])}\n"
        f"net: {money(fee['net_cost'])}, \\${fee['net_cost_per_100_usdc_traded']:.2f} per \\$100 traded\n"
        "maker fees are refunded in each trade")

    hd = head(fig, "How the 9Ns5 wallets were funded",
              "Base and Solana   ·   USDC and Circle CCTP transfers   ·   each arrow is a set of public transactions")
    ka = "9Ns5 -> AE2J wallets"
    b = d["b87f"]
    footer(fig, ax, [f"Also into 9Ns5: {money(b['0x7e07_to_9Ns5'])} through the unlabelled address 0x7e07…ff1f, which 0xb87f "
                     f"paid {money(b['to_0x7e07'])}. 9Ns5 also bridged {money(h[ka]['usdc'])} to all {h[ka]['wallets']} "
                     "AE2J wallets.",
                     "Labels: DefiLlama's Limitless adapter (fee recipient, rewards distributor); limitless.exchange/token "
                     "(multisigs), with owners and thresholds read on chain.",
                     "Source: out/a06_funding_chain_evidence.csv lists every transaction of the first three hops; "
                     "refs/sources/safe_owners.json holds the Safe snapshots; make pull rebuilds every hop."])
    layout(fig, hd, ax)
    save(fig, "a06_limitless_flow")


if __name__ == "__main__":
    flow()
