"""
Binance daily ETH and BTC closes, to value the few early AMM trades settled in WETH or cbBTC.

api.binance.com is unreachable from the US.
Writes data/raw/binance/<SYMBOL>_1d.json.
"""

import json, os, urllib.request

from py.chain import BASE_GENESIS, BINANCE, END_BLOCK

START_MS = 1711929600000                                  # 2024-04-01 00:00 UTC.
END_MS = (BASE_GENESIS + 2 * END_BLOCK) * 1000


def main():
    os.makedirs(BINANCE, exist_ok=True)
    for symbol in ("ETHUSDT", "BTCUSDT"):
        url = (f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d"
               f"&startTime={START_MS}&endTime={END_MS}&limit=1000")
        rows = json.load(urllib.request.urlopen(url, timeout=60))
        with open(os.path.join(BINANCE, f"{symbol}_1d.json"), "w") as fh:
            json.dump({"endpoint": url, "rows": rows}, fh)
        print(symbol, len(rows), "days")


if __name__ == "__main__":
    main()
