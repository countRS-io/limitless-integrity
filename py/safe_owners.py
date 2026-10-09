"""
Owners and threshold of the Safe the fee recipient paid and of Limitless's three labelled multisigs.

Read from Coinbase's public Base RPC at the first and last fee-recipient transfer to the Safe and at the end of the study window.
Writes paper/refs/sources/safe_owners.json.
"""

import json, os, time

import requests

from py.chain import END_BLOCK, RPCS, SAFE, SOURCES, TRANSFERS

RPC = RPCS[0]
SAFES = {
    SAFE: "unlabelled; paid by Limitless's fee recipient",
    "0xef59e19b2e63661514f9cb002ced51806a66329c": "Strategy Multisig (limitless.exchange/token)",
    "0xe7394bea0e4ed9ddee5b59f80a9e47679d8bce66": "Investors Multisig (limitless.exchange/token)",
    "0xbdfab8ec975166d86c7b4a882ccae95437cdb00e": "Ecosystem Wallet (limitless.exchange/token)",
}


def call(to, data, block):
    for k in range(8):   # The public endpoint rate-limits, so back off and retry.
        r = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                     "params": [{"to": to, "data": data}, hex(block)]}, timeout=30).json()
        if "result" in r:
            return r["result"][2:]
        time.sleep(2 ** k)
    raise RuntimeError(r)


def owners(safe, block):
    d = call(safe, "0xa0e67e2b", block)
    n = int(d[64:128], 16)
    return sorted("0x" + d[128 + 64 * i + 24:128 + 64 * (i + 1)] for i in range(n)), int(call(safe, "0xe75235b8", block), 16)


def main():
    import pandas as pd
    t = pd.read_parquet(os.path.join(TRANSFERS, "fee_trail", "feerec_usdc_out.parquet"))
    t = t[(t.to == SAFE) & (t.block <= END_BLOCK) & (t.get("usdc", t.get("amount")) > 0)]
    blocks = {"first_transfer": int(t.block.min()), "last_transfer": int(t.block.max()), "end_of_window": END_BLOCK}
    out = {}
    for safe, label in SAFES.items():
        out[safe] = {"label": label}
        for name, b in blocks.items():
            o, th = owners(safe, b)
            out[safe][name] = {"block": b, "owners": o, "threshold": th}
    path = os.path.join(SOURCES, "safe_owners.json")
    json.dump({"rpc": RPC, "calls": "getOwners() 0xa0e67e2b, getThreshold() 0xe75235b8", "safes": out},
              open(path, "w"), indent=1)
    same = {json.dumps(v[n]["owners"]) for v in out.values() for n in blocks}
    print(path, "one owner set across all safes and blocks:", len(same) == 1)


if __name__ == "__main__":
    main()
