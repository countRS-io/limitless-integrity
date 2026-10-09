"""
Live progress bar for a HyperSync pull running in another process, read from the file hypersync.get_logs writes.

Usage: `python -m py.watch_pull [progress.json]`, by default the fee-trail pulls' progress file.
"""

import json, sys, time

from tqdm import tqdm

from py.pull_fee_trail import PROGRESS

PATH = sys.argv[1] if len(sys.argv) > 1 else PROGRESS


def read():
    try:
        return json.load(open(PATH))
    except (OSError, ValueError):
        return None


def main():
    while (p := read()) is None:
        print("waiting for", PATH, end="\r")
        time.sleep(3)
    while True:   # A chunked pull rewrites the file per chunk: one bar each, Ctrl-C to quit.
        a = p["a"]
        bar = tqdm(total=p["b"] + 1 - a, unit="blk", unit_scale=True, desc=f"blocks {a:,}+")
        while p["a"] == a:
            bar.update(p["at"] - a - bar.n)
            bar.set_postfix_str(f"{p['logs']:,} logs")
            time.sleep(3)
            p = read() or p
        bar.close()

if __name__ == "__main__":
    main()
