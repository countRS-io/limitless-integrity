"""
Constants shared by every script: paths, the study window, Base timing, public RPCs and contract addresses.
"""

import os, re

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
NORM = os.path.join(DATA, "norm")
TRANSFERS = os.path.join(DATA, "raw", "base_transfers")
BINANCE = os.path.join(DATA, "raw", "binance")
SOURCES = os.path.join(ROOT, "paper", "refs", "sources")

BASE_GENESIS = 1686789347   # Timestamp of Base block 0; blocks are exactly 2 s apart.
END_BLOCK = 51_907_242      # 2026-09-28 13:57 UTC: the end of the study window for every source.
CHUNK = 500_000             # Harvest chunk in blocks, about 11.6 days.
PULL_FROM = 24_000_000      # Transfer pulls start before Limitless's first fill at block 24,809,842.
CLUSTERS_FROM = 35_000_000  # Cluster-wallet pulls start before AE2J's first fill at block 35,591,508.

# Coinbase's public endpoints serve archive logs without a key and cap the response size, not the block range, so the range grows through quiet periods and halves on a 413.
RPCS = ["https://mainnet.base.org", "https://developer-access-mainnet.base.org"]
SPAN0, SPAN_MAX, GROW_BELOW = 2_000, 50_000, 3_000

USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# Limitless exchanges and how each was found (paper/refs/limitless_dossier.md).
# Nothing on chain ties UNLINKED, the 2024 exchange, to the other six, so the analysis leaves it out.
UNLINKED = "0x71aceb0c45f4d58a2549dd21f1adc8e86d2899ea"
EXCHANGES = {
    UNLINKED: "CTFExchange, deployed 2024-12-16 by 0xb260a005",
    "0xa4409d988ca2218d956beefd3874100f444f0dc3": "CTFExchange, deployed 2025-02-06 by 0xaae78342",
    "0xf1de958f8641448a5ba78c01f434085385af096d": "CTFExchange, deployed 2025-12-15 by 0xaae78342",
    "0x05c748e2f4dcde0ec9fa8ddc40de6b867f923fa5": "venue.exchange of live single markets, deployed 2025-12-17 by 0xaae78342",
    "0xe3e00ba3a9888d1de4834269f62ac008b4bb5c47": "venue.exchange of live group markets",
    "0x5a38afc17f7e97ad8d6c547ddb837e40b4aedfc6": "neg-risk CTF exchange (legacy), per DefiLlama's adapter",
    "0x46e607d3f4a8494b0ab9b304d1463e2f4848891d": "neg-risk CTF exchange v2, per DefiLlama's adapter",
}
CTF = "0xc9c98965297bc527861c898329ee280632b76e18"
# Every fee module in DefiLlama's adapter (paper/refs/sources/defillama_limitless_index.ts), v1 to v4, each with its neg-risk twin.
# The modules keep taker fees and refund maker fees.
FEE_MODULES = ["0x6d8a7d1898306ca129a74c296d14e55e20aae87d", "0x73fc1b1395ba964fea8705bff7ef8ea5c23cc661",
               "0xeecd2cf0ff29d712648fc328be4ee02fc7931c7a", "0x18b3e1192c01286050a0994bc26f7226ae4a483d",
               "0x5130c2c398f930c4f43b15635410047cbea9d6eb", "0xfeb646d32a2a558359419a1c9c5dfb47fd92dadb",
               "0xf94ef760884b0605e433853aed17da574160226e", "0x6978254f397b18cf946eed8cbaf3eee712a712b9"]
FEE_RECIPIENT = "0x88eaf31f9fe392002e0e818527f8259af92287b1"
REWARDS = "0xe895cae6b705d584b03cd82fdd57cf7f8c52fadb"   # Rewards distributor: pays maker rebates.

# The money trail followed in a06 and a21.
SAFE = "0x7a0b16d55da33fa6bf1174532f33bba1914fac4c"   # 3-of-5 Safe, hop 2 of the a06 funding chain.
B87F = "0xb87f6670c965be9ecda4f5c8bfa7f5576658ed33"   # Pass-through from the Safe to 9Ns5.
X7E07 = "0x7e07a9148e9149e430c6412b79a675028595ff1f"  # Unlabelled; sent 9Ns5 $1.68M, and 0xb87f paid it $687k.
X6661 = "0x666101480cf996b88341c0b4972f7c3af9de049b"  # Takes most of the fee recipient's USDC and pays the rewards distributor.
MESSENGER = "0x28b5a0e9c621a5badaa536219b3a228c8168cf5d"   # CCTP TokenMessengerV2, same address on Base and Ethereum.
# USDC sent to TokenMinterV2 or TokenMessengerV2 is burned by Circle CCTP.
CCTP_BURN = {"0xfd78ee919681417d192449715b2594ab58f5d002", MESSENGER}
# The two Solana funders, as the 32-byte depositor in CCTP messages and in base58.
DEP_9NS5 = "7c774f222178f8e2d407dbfe683bf7755c0a998cd0fa1bd7f15fcc094f0598da"
DEP_AE2J = "890f35d9871ce937ec32b46a06ac2bfd9ffc4d4386630cbd23c76e3092e45a14"
FUNDERS = {DEP_9NS5: "9Ns5BaAG2oWJB2C1PgEpHeC3rBXLqJEmZKt7TQi4Nzuw",
           DEP_AE2J: "AE2JnkhVsi6Zu1pHCMah2JYjeugCEBiNYDn11q2STb5d"}


def flashloan_wallets():
    """The addresses on DefiLlama's list of Limitless flash-loan wallets, lower case."""
    with open(os.path.join(SOURCES, "defillama_flashloan_wallets.ts")) as fh:
        return {a.lower() for a in re.findall(r"0x[0-9a-fA-F]{40}", fh.read())}
