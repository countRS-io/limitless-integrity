"""
Shared constants and helpers for the analysis scripts.

Every script writes its result through emit(), so each number in the paper traces to one script and one run.
"""

import json, os, datetime

import numpy as np
import pandas as pd

# Re-exported from py/chain.py so the analysis scripts import them from here.
from py.chain import (DATA, NORM, TRANSFERS, BINANCE, SOURCES, BASE_GENESIS, END_BLOCK, USDC, UNLINKED, EXCHANGES, CTF,
                      FEE_MODULES, REWARDS, SAFE, B87F, X7E07, CCTP_BURN, DEP_9NS5, FUNDERS, flashloan_wallets)

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
FLAT = 0.10   # A position is flat when its net is under this share of what was traded.
# The windows of Limitless's two rebate posts, each ending on the day of the post.
REBATE_WINDOWS = {"3_months_to_2026-06-09": ("2026-03-09", "2026-06-10"),
                  "4_months_to_2026-07-23": ("2026-03-23", "2026-07-24")}


def pulled(*path):
    """
    A pull under data/raw/base_transfers, cut at END_BLOCK.

    Rows read on Ethereum (CCTP burns, all in early 2026) carry Ethereum block numbers and are kept.
    """
    d = pd.read_parquet(os.path.join(TRANSFERS, *path))
    keep = d.block <= END_BLOCK
    return d[keep | (d.chain == "Ethereum")] if "chain" in d else d[keep]


def clusters():
    """Cluster name to its set of wallets, from out/a06_limitless_cluster_wallets.csv."""
    w = pd.read_csv(os.path.join(OUT, "a06_limitless_cluster_wallets.csv"))
    return {c: set(g.wallet) for c, g in w.groupby("cluster")}


def trail(name):
    """
    A fee-trail pull (py/pull_fee_trail.py), with the USDC or token amount in `amount` and the block's time in `time`.

    Zero-value transfers from look-alike addresses carry nothing and are dropped.
    """
    d = pulled("fee_trail", name + ".parquet").rename(columns={"usdc": "amount"})
    return d[d.amount > 0].assign(time=lambda x: block_time(x.block))


def block_time(block):
    """Base block number(s) to UTC timestamps (timezone-naive)."""
    return pd.to_datetime(BASE_GENESIS + 2 * pd.Series(block).values, unit="s")


def canon_map():
    """Each token id with its market (condition_id) and whether it is the market's canonical token, the lower of the market's two ids."""
    t = pd.read_parquet(os.path.join(NORM, "limitless_tokens.parquet"), columns=["token0", "token1", "condition_id"])
    pairs = pd.concat([t, t.rename(columns={"token0": "token1", "token1": "token0"})]).drop_duplicates("token0")
    canon = np.where(pairs.token0.map(int) < pairs.token1.map(int), pairs.token0, pairs.token1)
    return pd.DataFrame({"token_id": pairs.token0.values, "condition_id": pairs.condition_id.values,
                         "is_canon": pairs.token0.values == canon})


def canonical(f, cm):
    """
    Express every fill on one token per market (cm from canon_map), so buying one side and selling the other agree.

    Adds condition_id, is_canon and maker_delta.
    The maker's position in the canonical token moves by +shares when they buy it (or sell its complement); the taker's moves by the opposite amount, whether they sold it or minted against it.
    A token missing from the registry counts as canonical.
    """
    f = f.merge(cm, on="token_id", how="left")
    sign = np.where(f.maker_side == "BUY", 1, -1) * np.where(f.is_canon.ne(False), 1, -1)
    return f.assign(maker_delta=sign * f.shares)


def fee_usdc(f):
    """
    The fee on each fill record, in USDC.

    A SELL order's fee (maker_side is the order's side) is charged in USDC; a BUY order's is charged in outcome tokens, valued at the fill price usdc / shares (0 when shares is 0).
    """
    fee = f.fee_raw / 1e6
    return fee.where(f.maker_side == "SELL", (fee * f.usdc / f.shares.where(f.shares > 0)).fillna(0.0))


def ratio(a, b):
    """a / b as a float, or None when b is 0, so an empty selection gives no inf or NaN."""
    return float(a / b) if b else None


def result(name):
    """The result an earlier script wrote to out/<name>.json."""
    with open(os.path.join(OUT, f"{name}.json")) as fh:
        return json.load(fh)["result"]


def emit(name, payload):
    """Write a result with the script name and run time attached."""
    os.makedirs(OUT, exist_ok=True)
    doc = {
        "script": name,
        "run_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "result": payload,
    }
    with open(os.path.join(OUT, f"{name}.json"), "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True, default=str)
    return doc
