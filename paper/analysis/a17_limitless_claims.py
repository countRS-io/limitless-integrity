"""
Each dated volume claim by Limitless or the press against the on-chain total, with and without DefiLlama's flash-loan wallets.

Totals are in notional (outcome shares) and USD, with WETH and cbBTC collateral priced at Binance daily closes and other non-USDC collateral left unpriced.
Reads the order-book fills, AMM trades, Binance daily closes and DefiLlama's flash-loan list.
Writes paper/out/a17_limitless_claims.json and .csv.
"""

import json, os

import pandas as pd

from analysis.common import emit, BINANCE, NORM, OUT, UNLINKED, USDC, flashloan_wallets

NAME = "a17_limitless_claims"

PRICED = {"0x4200000000000000000000000000000000000006": "ETHUSDT",
          "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf": "BTCUSDT"}

# Kinds: cumulative is all volume before `end`, window is [start, end) and growth is the ratio of two windows.
CLAIMS = [
    dict(id="L1", date="2025-07-01", kind="cumulative", end="2025-07-01", value=250e6,
         text="over $250M in bets on unique contracts",
         source="https://www.mexc.com/news/29350"),
    dict(id="L2", date="2025-10-20", kind="cumulative", end="2025-10-20", value=500e6,
         text="surpassed $500M in total trading volume",
         source="https://chainwire.org/2025/10/20/limitless-prediction-market-closes-10m-seed-round-ahead-of-lmts-token-launch/"),
    dict(id="L3", date="2025-10-20", kind="growth", a=("2025-08-01", "2025-09-01"), b=("2025-09-01", "2025-10-01"),
         value=25.0, text="trading volume grew 25x between August and September",
         source="https://chainwire.org/2025/10/20/limitless-prediction-market-closes-10m-seed-round-ahead-of-lmts-token-launch/"),
    dict(id="L4", date="2025-10-20", kind="window", start="2025-10-01", end="2025-10-16", value=100e6,
         text="$100M+ notional volume by mid-October, surpassing September",
         source="https://chainwire.org/2025/10/20/limitless-prediction-market-closes-10m-seed-round-ahead-of-lmts-token-launch/"),
    dict(id="L5", date="2026-04-20", kind="window", start="2026-03-01", end="2026-04-01", value=1e9,
         text="crossed $1B monthly notional volume (month not named; compared with March, the last full month before publication)",
         source="https://bitcoinfoundation.org/news/prediction-markets/prediction-market-limitless-volume-base/"),
    dict(id="L6", date="2026-05-01", kind="window", start="2026-04-01", end="2026-05-01", value=1.5e9,
         text="over $1.5B monthly volume in April (CEO)",
         source="https://x.com/cjhtech/status/2050266878749331653"),
    dict(id="L7", date="2026-05-05", kind="window", start="2026-04-01", end="2026-05-01", value=1.66e9,
         text="$1.66B April notional (Dune, as reported)",
         source="https://defirate.com/news/limitless-files-cftc-approval-after-record-1-66b-month/"),
    dict(id="L8", date="2026-05-05", kind="cumulative", end="2026-05-01", value=3.9e9,
         text="about $3.9B cumulative notional (Dune, as reported)",
         source="https://defirate.com/news/limitless-files-cftc-approval-after-record-1-66b-month/"),
    dict(id="L9", date="2026-05-25", kind="window", start="2026-01-26", end="2026-05-26", value=4e9,
         text="Season 3: $4B traded volume",
         source="https://x.com/trylimitless/status/2059026219593544133"),
    dict(id="L10", date="2026-06-17", kind="window", start="2026-05-01", end="2026-06-01", value=2e9,
         text="close to $2B monthly volume (Bernstein's figure, from a call with the CEO)",
         source="https://www.theblock.co/post/405086/limitless-ceo-no-prediction-market-platform-will-dominate-perpetual-futures-precedent"),
]


def _daily_close(symbol):
    """Binance daily closes (py/pull_binance.py)."""
    with open(os.path.join(BINANCE, f"{symbol}_1d.json")) as fh:
        rows = json.load(fh)["rows"]
    return pd.Series({pd.Timestamp(r[0], unit="ms", tz="UTC").normalize(): float(r[4]) for r in rows})


def _tape():
    """One table of trades from both venues: time, trader(s), notional shares, USD."""
    listed = flashloan_wallets()
    ob = pd.read_parquet(os.path.join(NORM, "limitless_fills.parquet"),
                         columns=["time", "maker", "taker", "shares", "usdc", "taker_leg", "exchange"])
    ob = ob[~ob.taker_leg & (ob.exchange != UNLINKED)]
    ob = pd.DataFrame({"time": ob.time, "venue": "orderbook", "notional": ob.shares, "usd": ob.usdc,
                       "flashloan": ob.maker.isin(listed) | ob.taker.isin(listed), "priced": True})
    amm = pd.read_parquet(os.path.join(NORM, "limitless_amm_trades.parquet"),
                          columns=["time", "who", "collateral", "collateral_amount", "outcome_tokens"])
    usd = amm.collateral_amount.where(amm.collateral == USDC)
    for token, sym in PRICED.items():
        px = _daily_close(sym)
        m = amm.collateral == token
        usd[m] = amm.collateral_amount[m] * amm.time[m].dt.normalize().map(px).values
    amm = pd.DataFrame({"time": amm.time, "venue": "amm", "notional": amm.outcome_tokens, "usd": usd.fillna(0),
                        "flashloan": amm.who.isin(listed), "priced": usd.notna()})
    return pd.concat([ob, amm], ignore_index=True)


def _totals(t):
    clean = t[~t.flashloan]
    return {"notional": float(t.notional.sum()), "usd": float(t.usd.sum()),
            "notional_ex_flashloan": float(clean.notional.sum()), "usd_ex_flashloan": float(clean.usd.sum()),
            "orderbook_notional": float(t[t.venue == "orderbook"].notional.sum()),
            "amm_notional": float(t[t.venue == "amm"].notional.sum()),
            "unpriced_trades": int((~t.priced).sum())}


def run():
    t = _tape()
    ts = lambda d: pd.Timestamp(d, tz="UTC")
    rows = []
    for c in CLAIMS:
        r = dict(c)
        if c["kind"] == "growth":
            a = _totals(t[(t.time >= ts(c["a"][0])) & (t.time < ts(c["a"][1]))])
            b = _totals(t[(t.time >= ts(c["b"][0])) & (t.time < ts(c["b"][1]))])
            for k in ("notional", "usd", "notional_ex_flashloan", "usd_ex_flashloan"):
                r[f"onchain_{k}"] = b[k] / a[k] if a[k] else None
            r["best_ratio"] = c["value"] / max(r["onchain_notional"], r["onchain_usd"])
        else:
            lo = ts(c["start"]) if c["kind"] == "window" else t.time.min()
            w = _totals(t[(t.time >= lo) & (t.time < ts(c["end"]))])
            r.update({f"onchain_{k}": v for k, v in w.items()})
            r["best_ratio"] = c["value"] / max(w["notional"], w["usd"])
            r["best_ratio_ex_flashloan"] = c["value"] / max(w["notional_ex_flashloan"], w["usd_ex_flashloan"])
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "a17_limitless_claims.csv"), index=False)
    return {"claims": rows, "first_trade": str(t.time.min()), "last_trade": str(t.time.max()),
            "trades": int(len(t)), "unpriced_trades": int((~t.priced).sum())}


if __name__ == "__main__":
    emit(NAME, run())
