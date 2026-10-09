"""
House figure style for the Limitless figures: colours, type sizes, date and money formats, and helpers that place the title block, legend, footnote and countRS mark.

Figures are drawn WIDTH inches wide and printed at about 6.5 in, so the type sizes below print at 7 pt or more.
"""

import os
import pandas as pd

FIG = os.path.join(os.path.dirname(__file__), "..", "fig")
WIDTH = 8.0

SURFACE = "#fcfcfb"
INK, INK_2, INK_3 = "#0b0b0b", "#52514e", "#84837c"
GRID, SPINE = "#e6e5e0", "#d8d7d1"

# One colour per meaning, in every figure.
BLUE = "#2a78d6"      # 9Ns5 wallets.
ORANGE = "#eb6834"    # AE2J wallets.
AQUA = "#1baf7a"      # Flash-loan wallets.
GREY = "#b8b7b0"      # Everyone else.
HOPS = ("#3d2a6b", "#7b5aa6", "#b391d6")   # Funding hops before 9Ns5, in chain order.
SIDE = "#9a6b2f"      # Side route into 9Ns5 (0x7e07).
REBATE = "#c2397a"    # Rebates paid by Limitless's rewards distributor.
RETURN = "#c0262d"    # USDC sent back to 9Ns5.

TITLE, SUB, TEXT, LABEL, FOOT = 13, 10, 9, 9.5, 8   # Title, subtitle, ticks and legend, axis labels, footnote.


def day(t, year=False):
    """'11 May', or '11 May 2026' with year=True."""
    t = pd.Timestamp(t)
    return f"{t.day} {t:%b}" + (f" {t.year}" if year else "")


def span(a, b, year=True):
    """'11 to 14 May 2026', '29 May to 2 Jun 2026', '1 Dec 2025 to 13 May 2026'."""
    a, b = pd.Timestamp(a), pd.Timestamp(b)
    y = f" {b.year}" if year else ""
    if a.year != b.year:
        return f"{day(a, True)} to {day(b, True)}"
    if a.month == b.month:
        return f"{a.day} to {day(b)}{y}"
    return f"{day(a)} to {day(b)}{y}"


def money(v):
    """'$481k' under a million, '$2.38M' and '$1.30B' above; the $ is escaped for matplotlib."""
    if v >= 1e9:
        return f"\\${v / 1e9:.2f}B"
    if v >= 1e6:
        return f"\\${v / 1e6:.2f}M"
    return f"\\${v / 1e3:,.0f}k"


def new_fig(height):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(WIDTH, height), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    return fig


def axes(fig, rect):
    ax = fig.add_axes(rect)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=INK_2, labelsize=TEXT, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(SPINE)
    return ax


def head(fig, title, sub):
    return [fig.text(0.5, 0.95, title, color=INK, fontsize=TITLE, fontweight="bold", ha="center", va="top"),
            fig.text(0.5, 0.90, sub, color=INK_2, fontsize=SUB, ha="center", va="top")]


def top_legend(ax, ncol, handles=None):
    """Legend centred above ax, in drawing order unless handles are given; layout() places it."""
    h, lab = ax.get_legend_handles_labels()
    if handles is not None:
        h, lab = handles, [x.get_label() for x in handles]
    return ax.legend(h, lab, loc="upper center", ncol=ncol, fontsize=TEXT, frameon=False, labelcolor=INK_2,
                     borderaxespad=0, columnspacing=1.6, handlelength=1.6)


def layout(fig, head, ax, leg=None):
    """
    Centre the title, subtitle and legend, and split the space above the axes into equal gaps: top edge to title, subtitle to legend, legend to axes.

    Call after everything is drawn on the axes.
    """
    fig.canvas.draw()   # Nothing has a position until drawn.
    r, H = fig.canvas.get_renderer(), fig.bbox.height
    ext = [a.get_window_extent(r) for a in head]
    block = (max(e.y1 for e in ext) - min(e.y0 for e in ext)) / H
    lh = leg.get_window_extent(r).height / H if leg else 0.0
    ax_top = (ax.get_window_extent(r) if ax.axison else ax.get_tightbbox(r)).y1 / H   # A diagram with axes off uses its drawn top.
    gap = (1 - ax_top - block - lh) / (3 if leg else 2)
    shift = (1 - gap) - max(e.y1 for e in ext) / H
    for a in head:
        a.set_y(a.get_position()[1] + shift)
    if leg:
        leg.set_bbox_to_anchor((0.5, ax_top + gap + lh), transform=fig.transFigure)


def _wrap(fig, r, text, maxw):
    """Break text into lines no wider than maxw (figure fraction)."""
    t = fig.text(0, 0, "", fontsize=FOOT)
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}" if cur else word
        t.set_text(trial)
        if cur and t.get_window_extent(r).width / fig.bbox.width > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    t.remove()
    return "\n".join(lines)


def footer(fig, ax, paragraphs, maxw=0.82):
    """
    Footnote centred midway between the lowest decoration of ax and the bottom edge, wrapped clear of the countRS mark at bottom right.

    The notes run on as one paragraph, a list given as items is numbered inline as 1) ...; 2) ..., and the source starts its own line.
    """
    parts = [" ".join(f"{k}) {x};" for k, x in enumerate(p, 1))[:-1] + "." if isinstance(p, list) else p for p in paragraphs]
    notes, _, source = " ".join(parts).partition("Source:")
    fig.canvas.draw()
    r, H = fig.canvas.get_renderer(), fig.bbox.height
    style = dict(color=INK_2, fontsize=FOOT, va="bottom", ha="center", multialignment="center", linespacing=1.4)
    texts = [fig.text(0.5, 0, _wrap(fig, r, x, maxw), **style) for x in (notes.strip(), "Source:" + source if source else "") if x]
    heights = [t.get_window_extent(r).height / H for t in texts]
    gap = FOOT / 72 * fig.dpi / H   # One line of space between the notes and the source.
    block = sum(heights) + gap * (len(texts) - 1)
    y = (ax.get_tightbbox(r).y0 / H - block) / 2
    for t, h in zip(reversed(texts), reversed(heights)):
        t.set_y(y)
        y += h + gap
    fig.text(0.975, 0.016, "countRS", color=INK_3, fontsize=TEXT, fontweight="bold", ha="right", va="bottom")
    return texts


def save(fig, name):
    import matplotlib.pyplot as plt
    os.makedirs(FIG, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), facecolor=SURFACE)
    plt.close(fig)
    print("wrote", os.path.abspath(os.path.join(FIG, f"{name}.png")))
