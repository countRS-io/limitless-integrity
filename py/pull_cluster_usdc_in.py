"""
Every USDC Transfer into the 9Ns5 and AE2J cluster wallets on Base.

Reads the wallets from paper/out/a06_limitless_cluster_wallets.csv.
Writes data/raw/base_transfers/cluster_usdc_in_all.parquet and a provenance file.
"""

import json, os, datetime

from py.chain import CLUSTERS_FROM, END_BLOCK, TRANSFERS
from py.pull_fee_trail import by_wallets, cluster_wallets


def main():
    wallets = cluster_wallets()
    df = by_wallets("cluster_usdc_in_all", 2, wallets, CLUSTERS_FROM, END_BLOCK, base=TRANSFERS)
    out = os.path.join(TRANSFERS, "cluster_usdc_in_all.parquet")
    df.to_parquet(out, index=False)
    json.dump({"pulled_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "Envio HyperSync, Base",
               "query": f"USDC Transfer logs to {len(wallets)} cluster wallets, blocks {CLUSTERS_FROM} to {END_BLOCK}",
               "rows": len(df)}, open(out.replace(".parquet", "_provenance.json"), "w"), indent=1)
    print(len(df), "rows")


if __name__ == "__main__":
    main()
