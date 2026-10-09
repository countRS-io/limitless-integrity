"""
Figures for the chronology and mechanism sections of the paper.

Reads results in paper/out (a06, a08, a11, a16, a17, a19), the CCTP mint and burn pulls under data/raw/base_transfers, and two lists under paper/refs/sources.
Writes paper/fig/a20_*.png and paper/fig/a20_*.pdf.
"""

import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from analysis.style import (SURFACE, INK, INK_2, INK_3, GRID, BLUE, ORANGE, AQUA, GREY, HOPS, SIDE, REBATE, RETURN,
                            TEXT, LABEL, day, span, money, new_fig, axes, head, top_legend, layout, footer, save)
from analysis.common import (OUT, END_BLOCK, B87F, X7E07, DEP_9NS5, block_time, clusters, flashloan_wallets, pulled,
                             result)
from analysis.a06_limitless_figure import safe_peers, joined

END = block_time(END_BLOCK)[0]
FEES_FROM = pd.Timestamp("2026-02-16")   # Week of the first 9Ns5 fill.


def _whole_weeks(df):
    """Drop weeks that run past the end of the study window; also return the first dropped week."""
    keep = df.week + pd.Timedelta(days=7) <= END
    return df[keep].reset_index(drop=True), df.week[~keep].min()


def _sets():
    """The 9Ns5 wallets ordered by first trade, and the row where the second set starts (the longest gap between consecutive first trades)."""
    wl = pd.read_csv(os.path.join(OUT, "a19_wallets.csv"), parse_dates=["first_fill", "last_fill"])
    wl = wl[wl.cluster == "9Ns5"].sort_values(["first_fill", "last_fill"]).reset_index(drop=True)
    wl["first_fill"] = wl.first_fill.dt.tz_convert(None)
    return wl, int(wl.first_fill.diff().idxmax())


def _returned():
    """CCTP burns on Base from the 9Ns5 wallets back to 9Ns5."""
    b = pulled("fee_trail", "burns_to_9ns5.parquet").rename(columns={"frm": "sender", "amount": "usdc"})
    b = b[b.chain == "Base"].assign(time=lambda d: block_time(d.block))
    return b


def _groups():
    """The four series of the timeline and the unwind figure, in stacking (and legend) order."""
    c = clusters()
    flash = flashloan_wallets()
    return [("9Ns5", BLUE, f"order book, 9Ns5 wallets on both sides ({len(c['9Ns5'])})"),
            ("AE2J", ORANGE, f"order book, AE2J wallets on both sides ({len(c['AE2J'])})"),
            ("flash", AQUA, f"AMM, the {len(flash)} flash-loan addresses DefiLlama excludes"),
            ("other", GREY, "everyone else")]


def _events(ax, events, top, close=None):
    """A dotted line and a numbered marker per event; a marker within `close` of the one before it is raised a step so the two do not touch."""
    prev, lift = None, 0
    for k, (t, _) in enumerate(events, 1):
        t = pd.Timestamp(t)
        lift = 1 - lift if close is not None and prev is not None and t - prev < close else 0
        ax.axvline(t, color=INK_3, lw=0.9, ls=":", zorder=0)
        ax.text(t, top * (1 + 0.085 * lift), str(k), color=INK, fontsize=TEXT - 0.5, ha="center", va="bottom",
                bbox=dict(boxstyle="circle,pad=0.22", fc=SURFACE, ec=INK_3, lw=0.8))
        prev = t


def _event_items(events, year):
    return [f"{day(d, year)}: {t.replace('; ', ', ')}" for d, t in events]


def _month_axis(ax, fmt="%b %Y"):
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))


TIMELINE = [("2025-10-22", "LMTS token launch"),
            ("2026-01-26", "Points Season 3 starts"),
            ("2026-02-18", "First {n1} 9Ns5 wallets start; AE2J falls away"),
            ("2026-04-14", "Maker rebates raised to 100% of taker fees"),
            ("2026-05-01", "CEO posts the April 'record'; CFTC application filed"),
            ("2026-05-25", "Season 3 ends at '\\$4B'; critics in the CEO's thread; airdrop on 27 May"),
            ("2026-06-30", "Integrity report, AMM only"),
            ("2026-07-31", "July letter promises an LMTS plan within three months")]


def timeline():
    w = pd.read_csv(os.path.join(OUT, "a17_limitless_weekly.csv"), parse_dates=["week"])
    w, cut = _whole_weeks(w[w.week >= "2025-09-29"])
    _, k = _sets()
    events = [(d, t.format(n1=k)) for d, t in TIMELINE]
    vals = {"9Ns5": w.orderbook_9Ns5, "AE2J": w.orderbook_AE2J, "flash": w.amm_flashloan,
            "other": w.orderbook_other + w.amm_other}
    total = sum(vals.values()) / 1e6
    share = 1 - vals["other"] / 1e6 / total
    x = w.week + pd.Timedelta(days=3)

    fig = new_fig(8.4)
    ax = axes(fig, [0.085, 0.47, 0.87, 0.30])
    bx = axes(fig, [0.085, 0.335, 0.87, 0.10])
    bottom = 0
    for key, col, lab in _groups():
        ax.bar(x, vals[key] / 1e6, bottom=bottom, width=5.6, color=col, linewidth=0.4, edgecolor=SURFACE, label=lab)
        bottom = bottom + vals[key] / 1e6
    top = total.max() * 1.04
    _events(ax, events, top)
    ax.set_ylim(0, top * 1.13)
    ax.set_ylabel("outcome shares per week,\nmillions", color=INK_2, fontsize=LABEL)
    bx.fill_between(x, share * 100, step="mid", color=INK_3, alpha=0.25, linewidth=0)
    bx.step(x, share * 100, where="mid", color=INK, lw=1.3)
    for d, _ in events:
        bx.axvline(pd.Timestamp(d), color=INK_3, lw=0.9, ls=":", zorder=0)
    bx.set_ylim(0, 100)
    bx.set_yticks([0, 50, 100])
    bx.set_ylabel("three groups,\n% of volume", color=INK_2, fontsize=LABEL)
    for a in (ax, bx):
        a.set_xlim(w.week.min() - pd.Timedelta(days=4), w.week.max() + pd.Timedelta(days=10))
        _month_axis(a, "%b\n%Y")
    ax.set_xticklabels([])
    bx.set_xlabel("week (UTC)", color=INK_2, fontsize=LABEL, labelpad=6)
    h = head(fig, "Limitless weekly volume on Base, by who traded it",
             f"order book and AMM   ·   {span(w.week.min(), w.week.max() + pd.Timedelta(days=6))}   ·   "
             f"{total.sum() / 1e3:.2f}B outcome shares")
    leg = top_legend(ax, 2)
    footer(fig, bx, [_event_items(events, True),
                     "Bottom panel: share of each week's outcome shares traded by the three groups together. "
                     f"The partial week from {day(cut, True)} is left out.",
                     "Source: OrderFilled, FPMMBuy and FPMMSell logs on Base (a17); groups from Circle CCTP "
                     "messages (a06); flash-loan addresses from DefiLlama's Limitless adapter."])
    layout(fig, h, ax, leg)
    save(fig, "a20_timeline")


UNWIND = [("2026-05-19", "critic alleges wash trading"),
          ("2026-05-25", "Season 3 ends; CEO's 'farmed volume' thread"),
          ("2026-05-27", "Season 3 airdrop"),
          ("2026-06-04", "9Ns5 volume halves"),
          ("2026-06-30", "integrity report"),
          ("2026-07-05", "DefiLlama filter")]
UNWIND_SPAN = ("2026-04-01", "2026-07-31")


def unwind():
    d = pd.read_csv(os.path.join(OUT, "a19_daily_groups.csv"))
    a = pd.read_csv(os.path.join(OUT, "a19_amm_daily.csv"))
    ob = d.pivot_table(index="day", columns="group", values="contracts", aggfunc="sum").fillna(0)
    am = a.pivot_table(index="day", columns="group", values="contracts", aggfunc="sum").fillna(0)
    t = ob.join(am, how="outer").fillna(0)
    t.index = pd.to_datetime(t.index)
    t = t.loc[UNWIND_SPAN[0]:UNWIND_SPAN[1]] / 1e6
    vals = {"9Ns5": t["9Ns5_inside"], "AE2J": t["AE2J_inside"], "flash": t["amm_flashloan"]}
    vals["other"] = t.sum(axis=1) - sum(vals.values())
    wl, k = _sets()
    s2 = wl.first_fill.iloc[k:]
    size = result("a19_amm_clusters")["flashloan_last_day_over_1M_shares"]
    events = sorted([(s2.min().normalize(), f"{len(s2)} more 9Ns5 wallets start"),
                     (pd.Timestamp(size["day"]), "flash-loan wallets' last day of size")] +
                    [(pd.Timestamp(dd), tt) for dd, tt in UNWIND])
    r = result("a06_limitless_flow")["hops"]["wallets -> 9Ns5 (returned)"]
    r0, r1 = pd.Timestamp(r["first"]), pd.Timestamp(r["last"])

    fig = new_fig(6.6)
    ax = axes(fig, [0.085, 0.31, 0.87, 0.43])
    bottom = 0
    for key, col, lab in _groups():
        ax.bar(t.index, vals[key], bottom=bottom, width=0.8, linewidth=0.25, edgecolor=SURFACE, color=col, label=lab)
        bottom = bottom + vals[key]
    top = bottom.max() * 1.03
    ax.axvspan(r0 - pd.Timedelta(hours=12), r1 + pd.Timedelta(hours=12), color=RETURN, alpha=0.12, lw=0, zorder=0)
    ax.annotate(f"{r['wallets']} 9Ns5 wallets\nsend {money(r['usdc'])}\nback to 9Ns5", xy=(r1 + pd.Timedelta(hours=12), top * 0.86),
                xytext=(r1 + pd.Timedelta(days=9), top * 0.86), color=RETURN, fontsize=TEXT, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=RETURN, lw=0.8, shrinkA=2, shrinkB=0))
    _events(ax, events, top, close=pd.Timedelta(days=4))
    ax.set_ylim(0, top * 1.2)
    ax.set_xlim(t.index.min() - pd.Timedelta(days=1), t.index.max() + pd.Timedelta(days=1))
    _month_axis(ax, "%b")
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
    ax.tick_params(axis="x", which="minor", length=3, color=INK_3)
    ax.set_ylabel("outcome shares per day, millions", color=INK_2, fontsize=LABEL)
    ax.set_xlabel(f"day (UTC), {t.index.min().year}", color=INK_2, fontsize=LABEL, labelpad=6)
    h = head(fig, "Limitless daily volume, Apr to Jul 2026",
             f"order book and AMM   ·   {span(t.index.min(), t.index.max())}   ·   by who traded it")
    leg = top_legend(ax, 2)
    footer(fig, ax, [_event_items(events, False),
                     f"Shaded: the days on which {r['wallets']} of the {len(wl)} 9Ns5 wallets bridged USDC back to the "
                     f"Solana account that funded them ({span(r0, r1, year=False)}).",
                     "Source: OrderFilled, FPMMBuy and FPMMSell logs on Base (a19); CCTP transfers from the wallets "
                     "to 9Ns5 (a06)."])
    layout(fig, h, ax, leg)
    save(fig, "a20_unwind_daily")


def fees():
    f = pd.read_csv(os.path.join(OUT, "a19_weekly_fees.csv"), parse_dates=["week"])
    f, cut = _whole_weeks(f[f.week >= FEES_FROM - pd.Timedelta(days=7)])
    x = f.week + pd.Timedelta(days=3)
    fig = new_fig(6.2)
    ax = axes(fig, [0.085, 0.30, 0.87, 0.44])
    bottom, drawn = 0, []
    for col, c, lab in (("9Ns5_taker_fees", BLUE, "taker fees, 9Ns5 wallets"),
                        ("AE2J_taker_fees", ORANGE, "taker fees, AE2J wallets"),
                        ("other_taker_fees", GREY, "taker fees, everyone else")):
        drawn.append(ax.bar(x, f[col] / 1e3, bottom=bottom, width=5.6, color=c, linewidth=0, label=lab))
        bottom = bottom + f[col] / 1e3
    drawn += ax.plot(x, f["9Ns5_rewards_received"] / 1e3, color=REBATE, lw=2, marker="o", ms=4,
            markeredgecolor=SURFACE, markeredgewidth=1.0,
            label="9Ns5 rebates paid by Limitless's rewards distributor")
    top = max(bottom.max(), (f["9Ns5_rewards_received"] / 1e3).max()) * 1.25
    for d, text in (("2026-04-14", "maker rebates\nraised to 100%"), ("2026-05-25", "Season 3\nends"),
                    ("2026-06-30", "integrity\nreport")):
        tt = pd.Timestamp(d)
        ax.axvline(tt, color=INK_3, lw=0.9, ls=":", zorder=0)
        ax.text(tt + pd.Timedelta(days=2), top, text, color=INK_3, fontsize=TEXT, va="top", ha="left", linespacing=1.25)
    ax.set_ylim(0, top * 1.03)
    ax.set_xlim(f.week.min() - pd.Timedelta(days=2), f.week.max() + pd.Timedelta(days=8))
    _month_axis(ax)
    ax.set_ylabel("USDC per week, thousands", color=INK_2, fontsize=LABEL)
    ax.set_xlabel("week (UTC)", color=INK_2, fontsize=LABEL, labelpad=6)
    last = f.week.max() + pd.Timedelta(days=6)
    # The totals cover the whole window, including the part week the bars leave out (a19, a11).
    tf = result("a19_limitless_anatomy")["taker_fees"]["from_2026-02-16"]
    nine, venue = tf["9Ns5"], tf["venue"]
    back = result("a11_fee_timeline")["9Ns5"]["totals"]["rebates_and_rewards"]
    h = head(fig, "Who paid Limitless's taker fees, and what came back",
             f"order book   ·   weekly   ·   {span(f.week.min(), last)}")
    leg = top_legend(ax, 2, drawn)
    footer(fig, ax, [f"From {span(FEES_FROM, END)} the 9Ns5 wallets were charged {money(nine)} of the {money(venue)} "
                     f"in taker fees charged on the order book ({nine / venue:.0%}), and received {money(back)} back "
                     "in rebates.",
                     "Taker fees are read from each taker order's own OrderFilled record; a fee charged in outcome "
                     "tokens is valued at the fill price. Maker fees are refunded inside the same transaction and are "
                     f"left out. Gas is not counted. The partial week from {day(cut, True)} is left out.",
                     "Source: OrderFilled logs (taker fees) and USDC Transfer logs from Limitless's rewards distributor "
                     "0xE895…FaDB (rebates) on Base (a19, a11)."])
    layout(fig, h, ax, leg)
    save(fig, "a20_fees_rebates")


def _end_labels(ax, ends, gap):
    """
    Value labels at the right end of each line, pushed apart in y where two would overlap.

    A label whose line is crossed by another just to its right goes above the line's end instead.
    """
    ends = sorted(ends, key=lambda e: e[1])
    placed = []
    for x, y, text, col, above in ends:
        if above:
            ax.text(x, y + gap * 0.6, text, color=col, fontsize=TEXT, va="bottom", ha="right")
            continue
        for px, py in placed:
            if abs((x - px).days) < 45 and y - py < gap:
                y = py + gap
        placed.append((x, y))
        ax.text(x + pd.Timedelta(days=3), y, text, color=col, fontsize=TEXT, va="center", ha="left")


def money_timeline():
    ev = pd.read_csv(os.path.join(OUT, "a06_funding_chain_evidence.csv"), parse_dates=["time"])
    inbound = _returned()
    wallets = clusters()["9Ns5"]
    wl, k = _sets()
    mints = pulled("cctp_mints.parquet")
    mints = mints[(mints.depositor == DEP_9NS5) & mints.recipient.isin(wallets)]
    mints = mints.assign(time=lambda d: block_time(d.block), usdc=lambda d: d.amount)
    n_own, thr, peers = safe_peers()
    series = [
        (ev[ev.hop == "0x88ea -> Safe 0x7a0b"], HOPS[0], "fee recipient 0x88ea…87b1 to Safe 0x7a0b…ac4c"),
        (ev[ev.hop == "Safe 0x7a0b -> 0xb87f"], HOPS[1], "Safe 0x7a0b…ac4c to 0xb87f…ed33"),
        (inbound[inbound.sender == B87F], HOPS[2], "0xb87f…ed33 to 9Ns5 (Circle CCTP)"),
        (inbound[inbound.sender == X7E07], SIDE, "0x7e07…ff1f to 9Ns5 (Circle CCTP)"),
        (mints, BLUE, f"9Ns5 to the {len(wl)} 9Ns5 wallets (Circle CCTP)"),
        (inbound[inbound.sender.isin(wallets)], RETURN, "9Ns5 wallets back to 9Ns5 (Circle CCTP)"),
    ]
    tmin = min(d.time.min() for d, _, _ in series)
    tmax = max(d.time.max() for d, _, _ in series)
    ymax = max(d.usdc.sum() for d, _, _ in series) / 1e6 * 1.12
    fig = new_fig(6.6)
    ax = axes(fig, [0.085, 0.30, 0.83, 0.42])
    ends = []
    for d, col, lab in series:
        d = d.sort_values("time")
        ts = pd.concat([pd.Series([d.time.iloc[0] - pd.Timedelta(hours=1)]), d.time])
        cs = pd.concat([pd.Series([0.0]), d.usdc.cumsum() / 1e6])
        ax.step(ts, cs, where="post", color=col, lw=1.8, label=lab)
        soon = d.time.max() + pd.Timedelta(days=30)
        crossed = any(o.time.max() > d.time.max() + pd.Timedelta(days=1) and
                      o[o.time <= d.time.max()].usdc.sum() < d.usdc.sum() * 0.97 < o[o.time <= soon].usdc.sum()
                      for o, _, _ in series if o is not d)
        ends.append((d.time.iloc[-1], d.usdc.sum() / 1e6, money(d.usdc.sum()), col, crossed))
    _end_labels(ax, ends, ymax * 0.055)
    mark = -ymax * 0.07
    s1, s2 = wl.first_fill.iloc[:k], wl.first_fill.iloc[k:]
    for part, text, left in ((s1, f"first trades of {k} 9Ns5 wallets, {day(s1.min())}", True),
                             (s2, f"{len(s2)} more, {span(s2.min(), s2.max(), False)}", False)):
        ax.plot(part, np.full(len(part), mark), "|", color=BLUE, ms=8, mew=1.0)
        ax.text(part.min() - pd.Timedelta(days=4) if left else part.max() + pd.Timedelta(days=4), mark, text,
                color=INK_2, fontsize=TEXT, va="center", ha="right" if left else "left")
    ax.axhline(0, color=GRID, lw=0.8, zorder=0)
    ax.set_ylim(-ymax * 0.13, ymax)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(5))
    ax.set_yticks([v for v in ax.get_yticks() if 0 <= v <= ymax])
    ax.set_xlim(tmin - pd.Timedelta(days=7), tmax + pd.Timedelta(days=7))
    _month_axis(ax)
    ax.set_ylabel("cumulative USDC, millions", color=INK_2, fontsize=LABEL)
    ax.set_xlabel("time (UTC)", color=INK_2, fontsize=LABEL, labelpad=6)
    h9 = result("a06_limitless_flow")["hops"]["9Ns5 -> wallets"]
    h = head(fig, "The money behind the 9Ns5 wallets, hop by hop",
             "USDC on Base and Circle CCTP transfers to and from Solana account 9Ns5…Nzuw   ·   cumulative")
    leg = top_legend(ax, 2)
    footer(fig, ax, [f"The Safe has the same {n_own} owners and {thr}-of-{n_own} threshold as the {joined(peers)} "
                     "multisigs on Limitless's token page. "
                     f"9Ns5 bridged {money(h9['usdc'])} to the {h9['wallets']} wallets in {h9['transfers']:,} transfers; "
                     "each wallet's first trade is marked below the zero line.",
                     "Money is fungible: these lines show transfers and their timing, not which dollar ended where.",
                     "Source: out/a06_funding_chain_evidence.csv (fee recipient to Safe, Safe to 0xb87f); Circle CCTP mints and burns on Base "
                     "from the a06 pulls."])
    layout(fig, h, ax, leg)
    save(fig, "a20_money_timeline")


VMIN = 0.01   # Millions of shares; weeks below this are left blank.


def wallet_grid():
    ww = pd.read_csv(os.path.join(OUT, "a19_wallet_weekly.csv"), parse_dates=["week"])
    wl, k = _sets()
    n = len(wl)
    g = ww[ww.wallet.isin(wl.wallet)].groupby(["wallet", "week"]).contracts.sum().unstack().fillna(0)
    g = g.reindex(wl.wallet)
    weeks = pd.date_range(g.columns.min(), g.columns.max(), freq="7D")
    cut = weeks[weeks + pd.Timedelta(days=7) > END].min()
    weeks = weeks[weeks + pd.Timedelta(days=7) <= END]
    g = g.reindex(columns=weeks, fill_value=0)
    fig = new_fig(6.2)
    ax = fig.add_axes([0.10, 0.32, 0.76, 0.48])
    cax = fig.add_axes([0.88, 0.32, 0.014, 0.48])
    cmap = mcolors.LinearSegmentedColormap.from_list("blues", ["#dce8f8", "#7fb0ea", BLUE, "#174a8c"])
    cmap.set_bad(SURFACE)
    vals = np.ma.masked_less(g.values / 1e6, VMIN)
    im = ax.imshow(vals, aspect="auto", cmap=cmap, norm=mcolors.LogNorm(vmin=VMIN, vmax=vals.max()),
                   interpolation="nearest")
    ax.set_facecolor(SURFACE)
    ticks = [i for i in range(len(weeks)) if i == 0 or weeks[i].month != weeks[i - 1].month]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{weeks[i]:%b}" for i in ticks], color=INK_2, fontsize=TEXT)
    ax.set_yticks([0, k - 1, n - 1])
    ax.set_yticklabels(["1", str(k), str(n)], color=INK_2, fontsize=TEXT)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axhline(k - 0.5, color=INK_3, lw=0.8, ls=":")
    ax.set_ylabel("wallet, ordered by first trade", color=INK_2, fontsize=LABEL)
    ax.set_xlabel(f"week (UTC), {weeks[0].year}", color=INK_2, fontsize=LABEL, labelpad=6)
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.set_ticks([v for v in (0.01, 0.1, 1, 10, 100) if v <= vals.max()])
    cb.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
    cb.ax.yaxis.set_minor_locator(mticker.NullLocator())
    cb.ax.tick_params(colors=INK_2, labelsize=TEXT, length=0)
    cb.set_label("millions of shares traded that week (log scale)", color=INK_2, fontsize=TEXT)
    s1, s2 = wl.first_fill.iloc[:k], wl.first_fill.iloc[k:]
    r = result("a06_limitless_flow")["hops"]["wallets -> 9Ns5 (returned)"]
    back = set(_returned().sender) & set(wl.wallet)
    second = len(back & set(wl.wallet.iloc[k:]))
    where = (f"all from the second {n - k}" if second == len(back) else f"{second} of them from the second {n - k}")
    mk = wl.contracts_as_maker / (wl.contracts_as_maker + wl.contracts_as_taker)
    h = head(fig, f"The {n} 9Ns5 wallets, week by week",
             f"order book   ·   each row is one wallet, each column one week   ·   {span(weeks[0], weeks[-1] + pd.Timedelta(days=6))}")
    footer(fig, ax, [f"Rows 1 to {k} made their first trade on {day(s1.min())}; rows {k + 1} to {n} from "
                     f"{span(s2.min(), s2.max(), year=False)}, the week of the flash-loan wallets' last day of size. The first {k} "
                     f"went almost silent that same week. The {len(back)} wallets that sent USDC back to 9Ns5 on "
                     f"{span(r['first'], r['last'], year=False)} are {where}.",
                     f"Every one of the {n} wallets traded as both maker and taker, with between {mk.min():.0%} and "
                     f"{mk.max():.0%} of its shares as maker.",
                     f"Weeks under {VMIN * 1e6:,.0f} shares are blank; the partial week from {day(cut, True)} is left out.",
                     "Source: OrderFilled logs of Limitless's CTF exchanges on Base (a19); CCTP burns to 9Ns5 (a06)."])
    layout(fig, h, ax)
    save(fig, "a20_wallet_grid")


def flat():
    M = pd.read_csv(os.path.join(OUT, "a19_market_net.csv"))
    M = M[(M.condition_id != "?") & (M.gross > 0)]
    a08 = result("a08_self_crossing")
    FLAT = result("a16_limitless_volume")["flat_threshold"]
    okey = next(k for k in a08 if k.startswith("limitless_top"))
    top_n = re.search(r"\d+", okey).group()
    other = f"the {top_n} largest other Limitless wallets"
    bins = np.linspace(0, 1, 21)
    hist = {}
    for k in ("9Ns5", "AE2J"):
        r = (M[M.cluster == k].net.abs() / M[M.cluster == k].gross).clip(0, 1)
        hist[k] = (np.histogram(r, bins=bins)[0] / len(r) * 100, len(r))
    lo = 10 ** np.floor(np.log10(min(v[v > 0].min() for v, _ in hist.values())))
    fig = new_fig(6.0)
    ax = axes(fig, [0.085, 0.31, 0.87, 0.43])
    for k, col, lw in (("9Ns5", BLUE, 2.6), ("AE2J", ORANGE, 1.4)):
        v, m = hist[k]
        ax.stairs(np.maximum(v, lo), bins * 100, baseline=lo, color=col, lw=lw,
                  label=f"{k} wallets, taken as one trader ({m:,} markets)")
    ax.axvline(FLAT * 100, color=INK_3, lw=0.9, ls=":")
    ax.text(FLAT * 100 + 1, 60, f"flat: net position under\n{FLAT:.0%} of what was traded", color=INK_3,
            fontsize=TEXT, va="top")
    ax.set_xlim(0, 100)
    ax.set_yscale("log")
    ax.set_ylim(lo, 200)
    ax.yaxis.set_major_locator(mticker.LogLocator(numticks=10))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlabel("net position left in the market, % of shares traded there", color=INK_2, fontsize=LABEL, labelpad=6)
    ax.set_ylabel("% of the group's markets (log scale)", color=INK_2, fontsize=LABEL)
    o = a08[okey]["flat"]
    h = head(fig, "Where the 9Ns5 and AE2J positions ended, market by market",
             "order book   ·   every market each group traded   ·   5-point bins")
    leg = top_legend(ax, 2)
    footer(fig, ax, [f"Flat in {a08['9Ns5']['flat']['flat_markets_share']:.0%} of markets (9Ns5) and "
                     f"{a08['AE2J']['flat']['flat_markets_share']:.0%} (AE2J), against {o['flat_markets_share']:.0%} for "
                     f"{other} taken together. Net over gross across all markets: 9Ns5 "
                     f"{a08['9Ns5']['flat']['net_over_gross']:.1%}, AE2J {a08['AE2J']['flat']['net_over_gross']:.1%}, "
                     f"{other} {o['net_over_gross']:.1%}.",
                     "A bin with no markets is drawn on the bottom edge. Source: OrderFilled logs on Base, each fill "
                     "signed by its market's canonical outcome token (a19, a08)."])
    layout(fig, h, ax, leg)
    save(fig, "a20_market_flat")


if __name__ == "__main__":
    timeline()
    unwind()
    fees()
    money_timeline()
    wallet_grid()
    flat()
