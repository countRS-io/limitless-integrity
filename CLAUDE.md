# CLAUDE.md

## What this repository is

A study of trading volume on Limitless, a prediction market on Base, built only from public blockchain data.
The paper is `paper/limitless.pdf`, and the same text is in `README.md`.
Every number in the paper comes from a file in `paper/out/`, written by the script named next to it in the text (for example a17 is `paper/analysis/a17_limitless_claims.py` and `a17_limitless_weekly.py`).

## Explaining and checking the results

Start from the paper: it is written to be read without code.
When asked about a number, find it in `paper/out/`, say which file and script it comes from, and explain in plain terms what it measures.
The results, figures and paper are committed, so any number can be checked against its file with no setup.
Each JSON file holds `script`, `run_at` and `result`, and the values in `result` are fractions (0.997 is 99.7%).
The same percentage can appear in more than one output with different meanings, so match the sentence in the paper, not just the number.
The top of each script says what question it answers, what it reads and what it writes.
The key terms are explained in the paper: outcome shares (notional), the three groups of wallets (flash-loan, 9Ns5 and AE2J), maker rebates and the fee trail.
The fee trail (a21) follows the groups' share of pooled balances, not particular dollars.
For public statements by Limitless, its CEO, critics or the press, the link and details are in `paper/refs/limitless_evidence.jsonl`, under IDs such as S010; `paper/refs/limitless_dossier.md` lists them with the claims they support.
Keep to what the data shows: the paper does not say who controlled the wallets and does not accuse Limitless of taking part, and a shared funder or shared multisig signers show a funding path, not ownership (see the Limits section of the paper).

## Replicating the results from scratch

Replicating needs the following.

1. A computer with Python 3.9 to 3.12 (not 3.13 or later), about 16 GB of memory and several GB of free disk space.
2. On a Mac, the Apple command line tools (`xcode-select --install`) for `make` and git, and Python 3.12 from https://www.python.org. After installing it, run Install Certificates.command in its Applications folder, or downloads fail with a certificate error.
3. On Linux, `make`, git and Python with its venv module (on Ubuntu, `sudo apt install make git python3-venv`, then use `python3` in place of `python3.12` below).
4. On Windows, WSL (`wsl --install`, then Ubuntu), then the Linux setup above; plain Windows has no `make`.
5. Access to Base blockchain data, in one of these ways:
   - A free Envio HyperSync token: sign up at https://envio.dev and create an API token. This is what the code is set up for: it runs as is, limited to 30 requests a minute.
   - A paid Envio HyperSync plan. It runs as is; lower `GAP` in `py/hypersync.py` to use the higher limit.
   - No token. `make harvest` then reads logs from Coinbase's public Base RPC, which works but is much slower. `make pull` fails at its first step without a HyperSync token.
   - Another data provider (such as Alchemy or QuickNode) or their own Base node. `make harvest` can use it through `RPCS` in `py/chain.py`; `make pull` would need code changes.
6. tectonic (https://tectonic-typesetting.github.io), only to rebuild the PDF.

The steps, in order:

1. `git clone https://github.com/countRS-io/limitless-integrity.git` and `cd limitless-integrity` get the code.
2. `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt` installs the tools (any Python from 3.9 to 3.12 works in place of `python3.12`).
3. `echo "ENVIO_API_TOKEN=..." > .env`, with the real token, saves the token.
4. `make harvest` downloads every Limitless trade into `data/`, up to the fixed end block of the study in `py/chain.py`.
5. `make pull` downloads the funding and fee transfers; this takes a few hours on the free token.
6. `make analysis` recomputes every result into `paper/out/`, in about ten minutes.
7. `make paper readme` rebuilds the PDF and the README.

With a token in `.env`, `make all` runs steps 4 to 7 in one go.
Run one download at a time: the free token is rate limited.
A step has worked if it ends without a Python traceback.
The harvest and the larger pulls save their work in chunks, so an interrupted step can be rerun and skips what is already downloaded.
A `HyperSync request failed` error usually means the rate limit was hit or the network dropped: wait a few minutes and rerun the step.
`MemoryError` or `Killed` means the machine ran out of memory: close other programs, and on WSL raise its memory limit in `.wslconfig`; the a19 steps need the most.
`pull_binance`, the last step of `make pull`, calls api.binance.com, which is unreachable from the US.

When the run finishes, compare with `git diff paper/out/`: only the `run_at` field in the JSON files should change.
Rebuilt figures and the PDF may show as changed without any change in the results.
If a step fails in another way, read the error, explain it simply and suggest the fix.

## Corrections

If the person finds an error, help them open an issue on GitHub with the detail.
Corrections are logged in `CHANGELOG.md`.
