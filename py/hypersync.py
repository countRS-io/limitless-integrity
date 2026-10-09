"""
Bulk Base event logs from Envio HyperSync, returned in eth_getLogs form so every normaliser reads either source unchanged.

Needs ENVIO_API_TOKEN in .env; the free plan allows 30 requests a minute, so requests are spaced 2.1 s apart.
"""

import json, os, time

URL = "https://base.hypersync.xyz"
FIELDS = ["block_number", "log_index", "transaction_hash", "address", "data",
          "topic0", "topic1", "topic2", "topic3"]
GAP = 2.1


def token():
    env = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env):
        for line in open(env):
            if line.startswith("ENVIO_API_TOKEN="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return os.environ.get("ENVIO_API_TOKEN")


def available():
    return bool(token())


_last = [0.0]


def get_logs(address, topics, a, b, progress=None, more=(), url=URL):
    """
    Every log in blocks [a, b] from `address` (a list, or None for any) matching `topics`.

    `more` adds further (address, topics) selections to the same scan; a log matching any is returned once.
    `url` picks the chain (https://eth.hypersync.xyz for Ethereum).
    `progress`, a file path, gets the block reached and the log count after every page, for py.watch_pull.
    """
    import asyncio
    import hypersync as hs

    # Converts eth_getLogs topic filters (value, list of values or None) to HyperSync's list-per-position form.
    def selection(address, topics):
        if isinstance(address, str):
            address = [address]
        tsel = [[] if t is None else [t] if isinstance(t, str) else list(t) for t in topics]
        return hs.LogSelection(address=address, topics=tsel) if address else hs.LogSelection(topics=tsel)

    sels = [selection(address, topics)] + [selection(ad, t) for ad, t in more]
    fields = hs.FieldSelection(log=FIELDS)

    async def run():
        client = hs.HypersyncClient(hs.ClientConfig(url=url, api_token=token()))
        out, lo = [], a
        while lo <= b:
            for attempt in range(8):
                wait = GAP - (time.time() - _last[0])
                if wait > 0:
                    await asyncio.sleep(wait)
                _last[0] = time.time()
                try:
                    r = await client.get(hs.Query(from_block=lo, to_block=b + 1, logs=sels, field_selection=fields))
                    break
                except Exception:
                    await asyncio.sleep(min(60, 5 * 2 ** attempt))
            else:
                raise RuntimeError(f"HyperSync request failed at block {lo}")
            for l in r.data.logs:
                out.append({
                    "address": l.address.lower(),
                    "topics": [t for t in l.topics if t],
                    "data": l.data,
                    "blockNumber": hex(l.block_number),
                    "transactionHash": l.transaction_hash,
                    "logIndex": hex(l.log_index),
                })
            if r.next_block <= lo:
                raise RuntimeError(f"HyperSync made no progress at block {lo}")
            lo = r.next_block
            if progress:
                with open(progress, "w") as fh:
                    json.dump({"a": a, "b": b, "at": min(lo, b + 1), "logs": len(out)}, fh)
        return out

    return asyncio.run(run())


def get_logs_chunked(address, topics, a, b, parts, decode, chunk=1_000_000, progress=None, more=(), url=URL):
    """get_logs over [a, b] in chunks aligned to multiples of `chunk`, each decoded to a DataFrame and saved under `parts`, so a rerun skips finished chunks."""
    import pandas as pd

    os.makedirs(parts, exist_ok=True)
    lo = a
    while lo <= b:
        hi = min((lo // chunk + 1) * chunk - 1, b)
        part = os.path.join(parts, f"{lo}_{hi}.parquet")
        if not os.path.exists(part):
            df = decode(get_logs(address, topics, lo, hi, progress=progress, more=more, url=url))
            df.to_parquet(part, index=False)
            print(os.path.basename(parts), lo, hi, len(df), "rows", flush=True)
        lo = hi + 1
    files = sorted(f for f in os.listdir(parts) if f.endswith(".parquet"))
    keep = [f for f in files if a <= int(f.split("_")[0]) and int(f.split("_")[1].split(".")[0]) <= b]
    return pd.concat([pd.read_parquet(os.path.join(parts, f)) for f in keep], ignore_index=True)
