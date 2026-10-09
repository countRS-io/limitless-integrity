# Limitless (limitless.exchange): claims vs public record

Research dossier for a piece on market manipulation and wash trading. Compiled 2026-09-28.

> This is the research file as compiled on 28 September 2026 and is not kept up to date. The paper (`paper/limitless.tex`, rendered as the README) is the current text; where the two differ, the paper and the results in `paper/out/` hold. Its open items (section 7) are leads, not work in progress.

Scope: the company (Limitless Exchange, Limitless Labs, Limitless Markets US), the LMTS token, and public statements by co-founder and CEO CJ (Cameron) Hetherington in that role. His past ventures are out of scope.

Companion file: `limitless_evidence.jsonl`, 199 source records (S001 to S212, with gaps in the numbering; every statement the paper cites has its own record). Every factual statement below cites S-IDs from that file. Anything that is our own inference is marked as an analysis note (A-IDs, section 6).

---

## 0. How to read this file

**IDs**
- `S###`: source record in the JSONL. Fields: id, title, url, publisher, author, published, event_dates, source_type, credibility, access, retrieved, identity_check, summary, key_facts, numbers, claims (which C or X entries it supports), caveats.
- `C##`: claim-vs-record entry (section 4).
- `X##`: exclusion: a look-alike entity or misattribution to keep out of the piece (section 5).
- `A##`: analysis note: our inference from the record, not a source (section 6).

**Credibility of a source, as evidence for what it states**
- A: official Limitless or CJ publication, regulator filing, DAO record. Proves the statement was made, not that it is true.
- B: independent data platform or established outlet with its own reporting.
- C: aggregator, relay, AI summary, profile database, partner content, secondary write-up.
- D: named or pseudonymous third party on social media, uncorroborated.
- E: anonymous comment with no evidence attached.
- own: countRS's own posts, cited in the paper for context, not as evidence about Limitless.

**Access status in the JSONL**
- `read_fetch`: page fetched directly. `read_browser_logged_in`: read on X in a logged-in browser (2026-09-27 or 2026-09-28). `snippet`: seen only as a search result. `git_clone`: read from a clone of a public GitHub repo. `not_retrieved`: link known, content not read. A suffix `(search result text)` means only the search result text was read, `truncated` that it was cut off. `cited_as_published`: countRS's own post, cited as posted, not re-read.

**Framing rules used throughout**
- Each C entry gives the Claim (what Limitless or CJ said), the Record (what documents and data show), and the Gap between them. No labels such as "lie" or "fraud". Where the company's own later disclosure contradicts an earlier claim, the entry cites both.
- Allegations by third parties are kept, tagged by credibility, and never merged into the Record unless something else corroborates them.
- Quotes are paraphrased; any quoted fragment is under 15 words. Pull exact quotes from the source when writing.
- X links need a logged-in session to read reliably.
- Dates are UTC unless a source gives local time.

---

## 1. Key findings (record-backed)

1. **Own disclosure.** Limitless's integrity report (2026-06-30) says flash-loan wash trading on its AMM markets produced $2.7B of notional volume across 309 wallets/profiles, attributed to points-program abuse; its published Dune query covers 2026-04-01 to 2026-06-01. The letter's opening line separately mentions a single account manufacturing fake volume, without saying whether it is the same finding. [C04, C06; S001, S187]
2. **Headline numbers from inside that window were never restated.** April record month ($1.5B to $1.66B), $3.9B cumulative, #2 onchain / #3 global, +345% "fastest growing", Season 3 "$4B traded". DefiLlama, which now excludes the flash-loan wallets, shows April notional of $263.5M, lower than March's $462.0M (April USDC volume $102.8M). [C01 to C03; S060, S130, S031, S066, S032, S101]
3. **Critics described the mechanism five weeks before the report.** On 2026-05-21 an account writing as Polymarket (affiliation unconfirmed) asked why Limitless's notional was 13x its taker volume. On 2026-05-25 CJ posted a thread framing "farmed volume" as a haters' talking point; a reply in that thread described add-liquidity, buy, sell, remove-liquidity in one block across 7 markets and cited a tx hash. [C04, C05; S112, S066, S111]
4. **Only the AMM was cleaned.** The report covers AMM (FPMM) markets. DefiLlama's filter (merged 2026-07-05, PR #7969, 328 addresses) also removes AMM trades only. No public filtering of order-book (CLOB) volume is documented. [C06; S001, S102, S202]
5. **"Revenue" is gross taker fees, passed through.** $20M then $40M "annualized revenue" and the "$3.4M May" figure are gross fees. CJ told a Bernstein-hosted call that 100% of revenue is rebated to market makers; Limitless says it paid $9.2M of maker rebates in four months, against $9.30M of DefiLlama gross fees for April to July. DefiLlama booked gross fees as protocol revenue until 2026-08-10 (PR #8676). Holders revenue is zero. [C10, C11; S060, S037, S071, S134, S051, S101, S202, A03]
6. **Incentive design made cross-account self-matching close to fee-neutral for a dominant maker (analysis, A02).** From 2026-04-14 makers got 100% rebates on the main crypto markets; self-trade prevention only works inside one profile; the rebate docs describe no same-owner exclusion. Limitless's own developer docs call matching between two profiles you control wash trading. [C07; S010, S012, S016, A02]
7. **Unexplained step change on 2026-04-25.** In DefiLlama's adjusted data (flash-loan wallets removed), daily USDC volume went from $1.67M (Apr 24) to $10.5M (Apr 25) and $17.7M (Apr 26), 11 days after rebates went to 100%. [A04; S101]
8. **World Cup "$1M".** The launch post said "up to" $1M; later posts dropped the qualifier ("the $1,000,000 pool"). The rules made $1M a ceiling on a pool starting at $100K that scaled with trader count, with payouts "completed by 3 August 2026". On 3 August Limitless said standings had been recalculated and payouts had only started. Final pool size was never published. Participants allege real users were removed while ambassador wallets with similar trading stayed. [C21; S056, S188, S189, S203, S191, S192]
9. **Token.** Stealth TGE with a company liquidity wallet selling into launch demand; weekly buybacks reported only until December 2025; token about 91% below its CryptoRank ATH and below the $0.075 public sale price; allocation table changed with no change notice found; circulating supply on the official page is about 3.4x what trackers use. CJ promised an LMTS plan on 2026-07-21 (no date given) and the July Huddle set a three-month token focus; no public follow-up as of 2026-09-28. [C12, C15 to C18, C20; S138 to S145, S106, S020, S175, S104, S077, S002, S003]
10. **Structure.** Users trade under Terms naming Street Chow Inc. (Panama); the CFTC applicant is a Delaware LLC wholly owned by Limitless Labs (Cayman); no public document found links Street Chow to Limitless Labs. The proposed US rulebook allows an exchange affiliate to make markets on both sides (with barriers). The application is still pending. [C27, C09, C30; S014, S091, S094, S090]

**Attribution cautions (do not overstate)**
- Limitless attributes the flash-loan activity to points-program abusers, not to itself. No public record ties the company or its staff to any wash-trading wallet. Critics accused the company itself (S110, S113); the disclosure confirmed only the AMM mechanism.
- Nothing public shows order-book wash trading; that claim rests on this repository's own analysis (a06, a08, a11), which shows a common funder and self-trading, not identity.
- The 90% share and "company is wash trading" claims by TheNotoriousSKi are one critic's estimates (D). He has a long public conflict with CJ and his own attribution varies (C26).
- The Bernstein "close to $2B" figure is attributed by The Block to Bernstein, not to Limitless (C08).
- The July LMTS plan window runs to about the end of October 2026 (C18).

---

## 2. Entities, people, handles, addresses

**Companies**
- **Limitless Exchange**: limitless.exchange, prediction market on Base; hybrid order book (CLOB) plus AMM (FPMM) markets. [S001]
- **Street Chow Inc.** (Panama): named as operator in the Terms of Service (updated 2026-09-15) and Privacy Policy (2025-03-19). Panama law, ICC arbitration in Panama City. [S014, S015, S161]
- **Limitless Labs**: Cayman Islands exempted entity, 2nd Floor Harbour Place, 103 South Church Street, George Town, Grand Cayman. Sole member of Limitless Markets US. Website limitless.network lists New York, Tokyo, Seoul and three units (Limitless Exchange, Limitless Markets US, Limitless Research). [S091, S023]
- **Limitless Markets US, LLC**: Delaware LLC formed 2026-01-26, initial capital $1, applicant for CFTC designated contract market (DCM) status, filed 2026-05-01, pending. Operating names "Limitless US", "Limitless Markets". Form DCM: principal office c/o Limitless Labs in Cayman, no physical US office. Rulebook Chapter 1 calls it "Limitless Labs US, LLC". [S090 to S094]
- **Limitless Research**: Japan and Korea research unit. [S023, S171]
- Data profiles place HQ in Grand Cayman (Crunchbase) or Lisbon (Tracxn), founding 2021, 2023 or December 2023. Vestbee calls it Ukrainian-founded. [S178, S152, S026]

**People (in their company roles)**
- Cameron "CJ" Hetherington: co-founder and CEO, X @cjhtech, LinkedIn cjhweb3; signed the Limitless Markets US operating agreement as CEO of Limitless Labs. [S091, S179]
- Co-founders per Vestbee: Roman Mogylnyi, Dmytro Horshkov, Rev Miller. [S152]
- Scot Halvorsen: Chief Regulatory Officer, Limitless Markets US (announced 2026-06-23; ex Cboe Futures Exchange, Tradition SEF, SIFMA, DTCC). [S044, S095]
- "Chris": Chief Compliance Officer (first name only in CJ's post). [S082]
- Henrich Tauber: Head of Business Development. [S003]
- Clarence Seedorf: brand ambassador for the World Cup (terms undisclosed). [S024]
- Investors in official releases: 1confirmation (lead, pre-seed and seed; founder Nick Tomaino), Collider, F-Prime, DCG, Coinbase Ventures, Node Capital, Arrington Capital, Maelstrom (Arthur Hayes, adviser), Paper Ventures, Public Works, Punk DAO, WAGMI Ventures, Flyer One, SID, Base Ecosystem Fund group on Echo. [S149 to S151]

**Handles**
- Official: @trylimitless. CEO: @cjhtech. Not @cjhetherington (X04).

**Token**
- LMTS on Base: `0x9EadbE35F3Ee3bF3e28180070C429298a1b02F93`, fixed supply 1,000,000,000, token name "Limitless Official Token". [S020, S108]
- Holder labels from the official token page (read 2026-09-27/28) [S020]:
  - Sablier Token Lockup 1 `0xe261B366f231B12FCB58D6BbD71e57fAEE82431D`: 380,566,867
  - Sablier Token Lockup 2 `0xc19a09A66887017F603E5dF420ed3Cb9a5c07C0A`: 254,099,824
  - Ecosystem Wallet `0xBDFAb8ec975166d86C7b4a882CcAe95437cDB00E`: 161,642,086
  - Unlabeled (TGE wallet) `0x3c583Be48D2796534f8FC8EA214674Ff055d01d7`: 34,375,000
  - Strategy Multisig `0xEF59e19b2e63661514F9cB002CED51806A66329c`: 29,099,900
  - Limitless: Liquidity `0xBF3132977d9801506deF8E927c4Ff06E5b0801d1`: 8,550,990
  - Investors Multisig `0xE7394bea0e4Ed9Ddee5b59F80A9e47679D8bcE66`: 6,234,872

**Exchange contracts on Base (from the DefiLlama adapter)** [S102]
- FPMM factories: `0x8e50578aca3c5e2ef5ed2aa4bd66429b5e44c16e` (v1), `0xc397d5d70cb3b56b26dd5c2824d49a96c4dabf50`
- CTF exchanges: `0xa4409d988ca2218d956beefd3874100f444f0dc3` (legacy), `0xf1de958f8641448a5ba78c01f434085385af096d` (v2), `0x05c748e2f4dcde0ec9fa8ddc40de6b867f923fa5` (v3)
- Neg-risk CTF exchanges: `0x5a38afc17f7e97ad8d6c547ddb837e40b4aedfc6`, `0x46e607d3f4a8494b0ab9b304d1463e2f4848891d`, `0xe3e00ba3a9888d1de4834269f62ac008b4bb5c47`
- Fee recipient (treasury): `0x88eaf31f9fE392002e0E818527f8259af92287b1`
- Rewards distributor (pays maker rebates, LP rewards, creator fees): `0xE895CaE6B705d584b03cd82Fdd57cf7F8c52FaDB`
- Conditional tokens: `0xC9c98965297Bc527861c898329Ee280632B76e18`
- Fee modules v1 to v4 and wrapped collateral addresses: see S102 and the adapter source.

**Integrity-report artifacts** [S001, S102, S202]
- Example wash tx (Base): `0xe19542e6b7f50638eea02c43eca08f888f0e3b8848f55af727f92243caed443c`
- Dune tables: `dune.limitless_exchange.dataset_flashloan_wallets`, `dune.limitless_exchange.dataset_flashloan_daily_volume`
- DefiLlama wallet list (328 addresses): `https://raw.githubusercontent.com/DefiLlama/dimension-adapters/master/dexs/limitless-exchange/flashloan-wallets.ts`
- Critic's example tx: `0x02e71256253919dbb522ec8cc6aefa003b5223efeb4e2b2087c1e6df82f40eee` [S111]

---

## 3. Timeline

- 2023-12: founding date on the careers page. [S026]
- 2024-09-17: $3M pre-seed led by 1confirmation. [S151]
- 2024-12: period of the anonymous "$21,000" allegation (posted 2025-08-12). [S158, S122]
- 2025-03-19: Privacy Policy names Street Chow Inc. (Panama). [S015]
- 2025-07-01: $4M round, $7M total; Arthur Hayes adviser. Points Season 1 starts. [S150, S174, S005]
- 2025-07-03: fees blog says the fee system punishes manipulation. [S008]
- 2025-07-25 to 2025-10-24: TheNotoriousSKi calls most volume fraudulent, metrics fake, praise paid. [S115 to S117]
- 2025-09-22: Season 2 starts. [S006]
- 2025-09-25: Limitless blog on market manipulation and wash trading. Kaito sale window opens (to 10-02). [S009, S106]
- 2025-10-08/09: Kaito sale results: about $200.97M committed for a $1M raise at $75M FDV. [S153, S154]
- 2025-10-14/15: CJ publishes Binance's alleged listing asks; Binance calls them false and threatens legal action. [S084, S146, S147]
- 2025-10-16 (about): Limitless lists a market on whether Binance lists LMTS in 2025 (resolved NO). [S027]
- 2025-10-20: $10M seed announced. [S149]
- 2025-10-21: tokenomics published. [S175]
- 2025-10-22: stealth TGE; wallet 0x3c58 gets 40M LMTS; liquidity wallet 0xBF31 sells into launch; CJ explains. [S140 to S143, S085, S138, S139]
- 2025-10 whitepaper (fee router, staking). [S021]
- 2025-11-01 / 11-04: early-metrics and valuation write-ups. [S165, S169]
- 2025-12-11 to 12-30: weekly $50K buybacks reported (3rd and 6th); none reported after. [S144, S145]
- 2026-01-26: Limitless Markets US LLC formed; Season 3 starts. [S091, S007]
- 2026-03-04/05: Coinbase announces and opens LMTS-USD. [S125, S170]
- 2026-04-01: start of the flash-loan Dune query window. [S001]
- 2026-04-02: DefiLlama starts tracking Limitless notional volume (PR #5764). [S202]
- 2026-04-14: maker rebates raised to 100% on daily, hourly and 15-minute crypto markets. [S010]
- 2026-04-16: CJ celebrates a $100M daily volume candle; posts investor feedback list. [S087, S086]
- 2026-04-20: press piece on "$1B monthly volume record". [S133]
- 2026-04-21: Delaware good standing certificate. [S091]
- 2026-04-22: about 85.37M LMTS unlock. [S109]
- 2026-04-25/26: adjusted daily USDC volume jumps from $1.67M to $10.5M and $17.7M. [S101, A04]
- 2026-04-28: DefiLlama adds AMM fees to Limitless fees and revenue (PR #6576). [S202]
- 2026-05-01: CFTC DCM application filed; CJ's April recap ($1.5B, $20M annualized, #2/#3). [S090, S060, S061]
- 2026-05-05: coverage of the filing and $1.66B April month; Bitcoin.com April taker data. [S130, S132, S136, S176]
- 2026-05-08: CJ: lowest FDV/revenue ratio across sectors. [S062]
- 2026-05-11: DeFi Rate: Limitless weekly fees down 79.6% while notional rose. [S131]
- 2026-05-16: open interest: Limitless $830K. [S103]
- 2026-05-19 to 05-23: TheNotoriousSKi alleges wash trading, plans an investigation. [S110, S113, S200]
- 2026-05-20: CJ on insider trading. [S063]
- 2026-05-21: Limitless surveys market makers; primo_data asks about 13x notional/taker. [S030, S112]
- 2026-05-25: Season 3 ends ($4B claim); Season 4 starts; CJ's "haters" thread and critics' replies; Binance "puppet" post; Lauris post. [S032, S031, S064 to S068, S111, S114, S199, S004]
- 2026-05-26: 100% rebates "live across all" daily, hourly, minutely markets; critic says the wash volume is one airdrop farmer. [S033, S201]
- 2026-05-27: Season 3 airdrop (3% of supply, 30M LMTS); 3.6M staked; CJ says liquidity is rising. [S034, S069, S035, S070]
- 2026-05-28/29: "$3.37M monthly fees", "$3.4M May", "$40M run rate"; revenue share chart. [S036, S071, S072]
- Week of 2026-05-25: peak adjusted weekly notional 355.6M; week of 2026-06-01: 253.1M. [S101]
- 2026-06-01: end of the flash-loan Dune query window. [S001]
- 2026-06-03/04: third-party valuation ranking; "$40M annualized revenue"; Noma; user-generated markets. [S126, S037, S054, S025]
- 2026-06-08 to 06-16: $1M fees in a week; top 20 by earnings; $7M+ rebates in 3 months; "only 100% rebates"; NAVI; Chainlink; Seedorf; Season 4 post; World Cup "$1M" launch; 1.17M users; "18 reasons". [S074, S038, S039, S040, S041, S042, S024, S004, S056, S076, S043, S055, S075]
- 2026-06-17: Bernstein call coverage ("close to $2B monthly"). [S134, S135]
- 2026-06-18 / 06-24 / 06-26: "$1M trading competition", "$1,000,000 pool", XP boost. [S188, S189, S045]
- 2026-06-23: CRO appointment. [S044]
- 2026-06-30 (22:18 UTC, last day of Q2): June Huddle with the integrity report. [S001, S187]
- 2026-07-01: hiring post (PR for Chinese-speaking markets, football social media, engineering, content). [S046]
- 2026-07-02: UEFA predictor game ($5,000 pool). [S190]
- 2026-07-03: The Block article updated. [S134]
- 2026-07-05: DefiLlama merges the flash-loan wallet filter (PR #7969). [S202]
- 2026-07-09 / 07-17 / 07-20: MM bot academy; USDC referral program; 72-hour doubled referral; Season 4 monthly reset. [S047, S048, S049, S050]
- 2026-07-19: World Cup campaign ends (22:00 London). [S203]
- 2026-07-21: CJ acknowledges heavy LMTS sell pressure after unlocks, promises a plan. [S077]
- 2026-07-23: "$9.2M maker rebates in four months"; Circle Seoul event. [S051, S079, S078]
- 2026-07-27 / 07-29: CJ on market capitulation; thanks Base and Coinbase Ventures. [S080, S081]
- 2026-07-31: July Huddle: three-month LMTS focus; World Cup about 10% of volume. Ambassador recruitment. [S002, S195]
- 2026-08-03: World Cup payout deadline per rules; 22:29 UTC Limitless says standings recalculated, payouts started. [S203, S191]
- 2026-08-04 to 08-13: payout complaints and allegations of selective removals. [S118, S119, S121, S192 to S194]
- 2026-08-05: CJ in Washington DC with CRO and CCO. [S082]
- 2026-08-06: changelog still describes 100% rebates on 15-minute crypto. [S010]
- 2026-08-10: DefiLlama books trader payouts as supply side (PR #8676); ParlayX partnership. [S202, S052]
- 2026-08-12: "rumors of being washed are exaggerated" (slang). [S053]
- 2026-08-17: CJ calls much onchain activity toxic and incentive-driven. [S083]
- 2026-08-26: disclosed partner deep dive on Substack. [S164]
- 2026-09-01: August Huddle, no token update. [S003]
- 2026-09-03 to 09-21: Arbitrum DAO bans "Limitless" (Limitless Finance, not this company). [S180, X01]
- 2026-09-08 / 09-14: $120K referral rewards in August; partners earned $200K+. [S197, S196]
- 2026-09-15: current Terms of Service. [S014]
- 2026-09-21: "5 weeks left" in Season 4. [S198]
- 2026-09-23: CJ interview ahead of EastPoint Seoul. [S171]
- 2026-09-27: LMTS at CryptoRank ATL $0.04213. [S106]
- 2026-10-22: next unlock event (about 96M incl. 83.33M team per CoinGecko widget). [S104]
- About 2026-10-26: Season 4 end. About 2026-10-31: end of the July three-month LMTS window. [S004, S198, S002]

---

## 4. Claims vs record

### A. Volume, growth and rank

#### C01. April 2026 "record month"
- **Claim.** CJ, 2026-05-01: over $1.5B monthly volume in April, #2 largest onchain prediction market, #3 globally including US regulated venues. [S060] CJ on LinkedIn (via DeFi Rate): $3.9B total, 300% month-over-month growth. DeFi Rate (Dune): $1.66B April notional vs $109M in September 2025, 5.6% market share. [S130] Casino.org (Dune): $204.9M in January to $1.66B in April. [S136] Press piece 2026-04-20: crossed $1B monthly, $35M to $40M daily. [S133] CJ 2026-04-16: celebrated a $100M daily candle. [S087]
- **Record.** Limitless's own report: flash-loan wash trading, $2.7B notional, Dune query window 2026-04-01 to 2026-06-01. [S001] DefiLlama with the flash-loan wallets excluded: April notional $263.5M and USDC volume $102.8M; March notional $462.0M, so April falls rather than peaks. Dune vs adjusted gap for April is about $1.4B. May 1 to 5: Dune $348.2M vs adjusted $57.4M. [S101] Adjusted daily notional on Apr 10 to 19 was $3.2M to $11.7M, not $35M to $40M. [S133 caveat, S101] Bitcoin.com (Dune): April taker volume $205M. [S132]
- **Gap.** Headline April figures are about 6x the adjusted notional and fall inside the window the company later identified. None has been corrected.
- **Strength.** High (company's own disclosure plus independent data).
- **Caveats.** Notional counts shares, not dollars (A01). Sep 2025 to Feb 2026 Dune and DefiLlama agree within 2%; March differs by 14% (unexplained). CJ did not say whether $1.5B was notional or USDC. The flash-loan share of April is inferred from the gap; Limitless did not publish a monthly split.

#### C02. Cumulative and Season 3 totals
- **Claim.** $3.9B cumulative (May 2026). [S130] Season 3 wrap: $4B traded, 280,000+ active traders, 4.5M trades. [S032, S155] Careers page: $3.5B+. [S026] Crypto Briefing: $5B cumulative. [S168]
- **Record.** DefiLlama cumulative notional $3.429B and USDC $1.467B as of 2026-09-28, i.e. five months later and with flash-loan wallets excluded. [S100] Season 3 window (Jan 26 to May 25) adjusted: notional $1.59B, USDC $447M. [S101]
- **Gap.** "$4B" for Season 3 vs $1.59B adjusted notional for the same window.
- **Strength.** High for the gap.
- **Caveats.** "Traded volume" was not defined. Flash-loan wallets explain most of the difference; whether they explain all of it is not established.

#### C03. Rank and growth
- **Claim.** #2 onchain, #3 global (May 1). [S060] "Fastest-growing prediction market in the world", +345% over three months (Feb to Apr). [S031, S066] Closing the gap with Polymarket and Kalshi. [S064]
- **Record.** April taker volume (Dune): Kalshi $5.42B, Polymarket $1.99B, predict.fun $579.2M, Opinion $376.2M, Limitless $205M (5th). [S132] Open interest mid-May: Kalshi $670M, Polymarket $491M, predict.fun $14M, Opinion $8.1M, SX Bet $1.6M, Limitless $830K. [S103] CJ's own May revenue-share chart: Polymarket 86.7% of $30.66M. [S072] Artemis's weekly crypto-market comparison has Kalshi and Polymarket at 100% combined. [S166] Adjusted Feb to Apr: notional $372.9M to $462.0M to $263.5M; USDC $72.5M to $91.0M to $102.8M (+42%). [S101]
- **Gap.** Rank and growth claims hold only on notional that included the flash-loan volume.
- **Strength.** High.
- **Caveats.** On unadjusted Dune notional, "#2 onchain" in April may have been literally true. The +345% chart's source is not named.

#### C04. Wash-trading criticism: dismissed; mechanism later disclosed
- **Claim / stance.** CJ, 2026-05-25: a thread framing the "farmed volume" charge as coming from haters, arguing Limitless spent only $3.7M on cash rewards since inception vs Polymarket's $44M in one month, and +345% vs +13% growth. [S066] Sarcastic post implying Polymarket's rewarded volume is farmed. [S065] Later: rivals' volume may be more inflated than it appears (Bernstein call). [S134] Much onchain activity is toxic and incentive-driven (2026-08-17, about Robinhood Chain). [S083]
- **Record.** Before the report: TheNotoriousSKi on May 19 (40% weekly volume drop, blatant wash trading), May 21, May 23 (plans an investigation, questions investor diligence), May 25 (over 90% of volume from one wash farm that adds liquidity, buys, sells and removes liquidity across 7 markets in the same block; example tx 0x02e7...), May 26 (one airdrop farmer). [S110, S113, S200, S111, S201] DeFi Rate on May 11 listed inflated volume among possible causes of fees falling 79.6% while notional rose. [S131] Then Limitless's June 30 report disclosed the same AMM mechanism, attributing it to points abusers: flash loans, sole LP, trading against own liquidity, fees recovered, $2.7B notional, 309 wallets/profiles. [S001, S187]
- **Gap.** The company publicly waved off the "farmed" criticism on May 25; on June 30 it disclosed the mechanism critics had described (not their claim that the company was behind it), without revisiting the earlier figures or the exchange with critics.
- **Strength.** High on sequence. Medium on what the company knew and when: the report says it acted on a community report plus internal analysis, with no detection date.
- **Caveats.** CJ's thread argued about incentives and did not specifically deny AMM flash-loan activity. SKi's 90% figure is his estimate; he alternately addresses CJ as the wash trader (S111, S113) and attributes the volume to one airdrop farmer (S201). Limitless attributes it to points abusers.

#### C05. The 13x notional/taker ratio
- **Claim.** CJ, replying in the same thread: no issue with rebates and LP rewards; expects the notional/taker ratio and fee take rate to improve as the marketplace matures. [S066]
- **Record.** primo_data, 2026-05-21: for the week of May 4, notional $600M was 13x taker USDC $44M, against about 2x for "our" venue (the account writes as Polymarket; affiliation unconfirmed). [S112] DeFi Rate: Kalshi, Polymarket, Polymarket US at 2.2x to 2.9x. [S131] DefiLlama adjusted for the week of May 4: notional $41.7M, USDC $19.0M, ratio 2.2x. Weekly adjusted ratios ran 4.6x to 5.4x from January to mid-April, then 1.6x to 3.4x. [S101]
- **Gap.** Once the flash-loan wallets are removed, the ratio for that week is ordinary; the 13x came from activity Limitless later called fake. The reply attributed it to marketplace immaturity.
- **Strength.** High.
- **Caveats.** primo_data writes as a competitor (unconfirmed) and asked a question rather than alleging. Implied price of the removed trades is in A01.

### B. Market integrity

#### C06. What the integrity report covers, and what it leaves out
- **Claim.** June 30 letter: on-chain actor(s) used Morpho flash loans to become the only LP in AMM markets, traded against their own liquidity, withdrew liquidity with the fees and repaid in one transaction; found after a community report plus internal analysis; accounts banned, points cut, volume removed from public stats, monitoring added. Opening line: a single account manufacturing fake volume. [S001, S187]
- **Record and gaps.**
  1. Scope: the letter calls Limitless a hybrid CLOB/AMM venue but reports abuse in AMM markets only and says nothing about wash trading on the order book. DefiLlama's filter excludes AMM trades only. No public filtering of order-book activity is documented. [S001, S102, S202]
  2. Timing: no activity dates beyond the SQL filter (Apr 1 to Jun 1). Published 22:18 UTC on the last day of Q2, five weeks after critics described the mechanism, one month after the Season 3 airdrop. [S187, S111, S034]
  3. Airdrop: says points were cut, not whether the wallets had already claimed Season 3 tokens (3% of supply, 30M LMTS, claim opened May 27). [S001, S034, S069]
  4. No restatement of the April record, $3.9B, Season 3 $4B or rank claims (C01 to C03).
  5. Count: 309 wallets/profiles in the report vs 328 addresses in DefiLlama's list since 2026-07-05; not reconciled. [S001, S202]
  6. "Single account" (opening) vs "actor(s)" and 309 wallets/profiles (report); the letter does not say whether these are one finding. [S001, S187]
  7. Context: in the same weeks Limitless surveyed market makers (May 21), moved 100% rebates to all short markets (May 26), said liquidity was rising (May 27, June 13), and promoted AI market-making bots (July 9). [S030, S033, S070, S075, S047]
- **Strength.** High (company text and code).
- **Caveats.** Silence about the CLOB is not evidence of CLOB wash trading. The Dune tables may contain dates and daily volumes (open item 2).

#### C07. Anti-manipulation rules vs incentive design
- **Claim.** Fee system designed to reward conviction and punish manipulation (2025-07-03). [S008] Educational post: wash trading banned in the US since the 1930s; on-chain recording and community auditing protect Limitless users. [S009] ToS section 7 bans wash trading, spoofing, layering, coordinated trading and multiple accounts, with forfeiture on "reasonable suspicion". [S014] Developer docs: matching between two profiles you control is wash trading, not a self-trade-prevention gap. [S016] CJ: insider trading exists in all markets and bad actors must be rooted out; insider trading is easy to catch. [S063, S134]
- **Record.** Only takers pay fees; makers trade free; AMM markets charge a flat 0.40%. [S011] Self-trade prevention works only within one profile. [S016] From 2026-04-14, makers received 100% of taker fees as rebates on daily, hourly and 15-minute crypto markets, pro-rata per market. [S010, S012, S033] The rebate docs describe no exclusion for fills with the same owner on both sides. [S012] Season 4 points reward volume, with "quality" language but no explicit wash rule. [S004] Referral tiers count the referrer's own maker plus taker volume. [S019] The flash-loan scheme was flagged publicly in May; the disclosure came at the end of June (C04).
- **Gap.** Stated prohibitions coexist with a fee design under which cross-wallet self-matching costs little and earns volume, points and tiers (A02); detection is the only barrier.
- **Strength.** High for the rules and design facts; the incentive effect is analysis (A02).
- **Caveats.** Rebates are pro-rata shares of a market's fee pool, not refunds of one's own fee. Points formulas are not public.

#### C08. What the CEO told investors and analysts
- **Claim.** Bernstein-hosted call reported 2026-06-17: close to $2B monthly volume (Bernstein's figure), users about 60% APAC and 30% Europe, not live for US customers, 100% of revenue rebated to market makers to prioritise growth, industry retention inflated by automated trading, rival volume may be more inflated than it appears. [S134] Crypto Briefing version: about $1B a month in early 2026; no platform will pass 50% share. [S135] CJ mocked a question investors ask (Hyperliquid) and listed two years of investor feedback. [S073, S086]
- **Record.** DefiLlama adjusted notional: May $698.9M, June $574.4M. [S101] The Block updated the article on 2026-07-03, after the integrity report, with no visible change to the $2B figure. [S134]
- **Gap.** The volume figure circulated to Bernstein's audience in June appears to include activity Limitless later classified as fake (inference; call date unknown).
- **Strength.** Medium.
- **Caveats.** The Block attributes $2B to Bernstein. The Block and Crypto Briefing conflict on the share threshold (90% vs 50%).

#### C09. The proposed US exchange's own rules
- **Claim.** Exhibit L: Rule 5.17 prohibits wash sales, pre-arranged and noncompetitive trades; surveillance real-time plus T+1 by an unnamed third-party regulatory services provider plus internal dashboards, targeting spoofing, layering, wash trading and momentum ignition; CRO reports to a Regulatory Oversight Committee. [S093]
- **Record.** Exhibit M Rule 2.12 lets an exchange affiliate trade as a member, posting liquidity on either or both sides, trading aggressively and passively for profit, capitalized by the holding company, sharing employees on the boards of the exchange, affiliate and holding company, with no obligation to trade; conditions include information barriers, separate systems and physical separation, capital not sourced from the exchange itself, and algorithms that are not "readily exploitable". Rules 3.3(b) and 3.5(b) bar intentional self-matching for FCM and introducing-broker customers. Chapter 4 market-maker program may give financial benefits and reduced fees. Rule 2.11 bars insider trading on material non-public information. Inconsistencies: CRO (Exhibit L) vs CCO (Rule 2.6(f)(4)) reporting to the committee; "Limitless Labs US, LLC" vs "Limitless Markets US, LLC". Exhibit U seeks confidential treatment for everything except Form DCM and Exhibits G, L, M. [S094, S090]
- **Relevance.** Shows how the company describes affiliate market making and wash-trade bans to the CFTC. Applies to the proposed US exchange only, not to limitless.exchange.
- **Strength.** High.
- **Caveats.** The affiliate is not named. Rule 5.17's full text (Exhibit M, from p. 53) was not retrieved.

### C. Revenue, rebates and users

#### C10. "Revenue" and "earnings"
- **Claim.** $20M annualized revenue (April). [S060] Lowest FDV/revenue ratio across prediction markets, perps, lending and spot DEXs (May 8). [S062] Record $3.37M monthly fees, +97%, top 5 fee generator on Base, "$10M is next" (May 28). [S036] Over $3.4M of May "trading fee revenue", $40M annualized run rate (May 29). [S071] $40M annualized revenue, +140% vs April, +500% vs January, posted over a ranking of LMTS as the most efficiently valued token by valuation/revenue (June 3/4). [S037, S126] Top 20 protocol by monthly earnings; $1M fees in one week (June 8/9). [S038, S074]
- **Record.** CJ told the Bernstein call that 100% of revenue is rebated to market makers. [S134] Limitless: $7M+ returned to traders in 3 months (June 9); $9.2M of maker rebates in 4 months (July 23). [S039, S051, S079] DefiLlama gross fees, April to July: $1.26M, $3.82M, $3.04M, $1.18M ($9.30M); August $0.57M; September to the 26th $0.19M. [S101] DefiLlama code: fees swept to the treasury are forwarded in full to traders; holders revenue hard-coded to zero; revenue booked equal to gross fees until 2026-08-10 (PR #8676). [S102, S202] After that change: payouts were 89% of fees (Aug 10 to Sep 26); 30-day revenue $33,157 vs fees $206,843. [S101, S100] A partner Substack's "Q2 revenue $8.11M" equals DefiLlama gross fees. [S164]
- **Gap.** "Revenue", "earnings" and valuation-to-revenue rankings were built on gross fees that the company itself says it passes to market makers.
- **Strength.** High.
- **Caveats.** Gross fees are a legitimate metric; the issue is labeling and omission. Which data source produced the "top 5" and "top 20" rankings is not established (open item 17). Whether wash activity inflated fees is separate (A05).

#### C11. "The only prediction market with 100% maker rebates"
- **Claim.** 100% rebates from 2026-04-14 (changelog) and "live across all daily, hourly and minutely markets" (May 26); "only prediction market with 100% market-making rebates across most markets" (June 9 and 10, LinkedIn about June 3); listed among "18 reasons". [S010, S033, S039, S040, S179, S043]
- **Record.** The live rewards page now shows 30% for BTC/ETH 5-minute and 15-minute markets (100% on daily equity markets such as OXY, ITA, EQT, LMT). [S013] The changelog entry of 2026-08-06 and the maker-rebates doc still describe 100% for 15-minute crypto. [S010, S013] No announcement of the cut was found.
- **Gap.** A reduction on the markets the claim was built on, with no announcement found; docs and live page disagree.
- **Strength.** High.
- **Caveats.** Rates are set per market and change over time; the date of the cut is unknown (open item 13).

#### C12. Token value accrual: fee router, buybacks, staking
- **Claim.** Whitepaper: a protocol fee share goes to an LMTS fee router; stakers receive fees in collateral or via periodic open-market LMTS purchases; staking lowers taker fees and improves maker rebates. [S021] Token page: part of platform fees funds buybacks, staking rewards and incentive pools. [S020] CJ (Oct 2025): 0xBF31 funds would buy back LMTS; buybacks had started. [S143] Staking APY 14.52%. [S020, S022] CJ promoted an Aerodrome LP APR around 1,301%. [S061]
- **Record.** DefiLlama: no portion of trading fees reaches LMTS holders on-chain; holders revenue $0. [S100, S102] Weekly $50K buybacks reported for 3 and then 6 weeks ($300K by 2025-12-30); no later reports; no buyback address or amounts on official pages; Tokenomist has no buyback data. [S144, S145, S020, S107] Staking yield source undisclosed; 15.4M LMTS staked now vs 3.6M announced on airdrop day. [S022, S035] The CEO says 100% of fee revenue goes to market makers, leaving nothing for a fee router. [S134]
- **Gap.** Advertised fee-to-token mechanics are not visible on-chain.
- **Strength.** Medium-high.
- **Caveats.** Buybacks could be unannounced; absence of reports is not proof (open item 7).

#### C13. "$3.7M of cash rewards since inception"
- **Claim.** CJ, May 25: $3.7M spent on cash rewards since inception, less than Polymarket's $44M in one month, and less than Limitless's lifetime capital raised. [S066]
- **Record.** Two weeks later: $7M+ of fees "distributed back to traders" in 3 months; later $9.2M of maker rebates in 4 months. Token incentives on top: Season 3 airdrop alone 30M LMTS. [S039, S051, S069]
- **Gap.** The $3.7M excludes maker rebates and token airdrops, which by the company's own numbers were larger.
- **Strength.** Medium (definitions not given).

#### C14. User counts
- **Claim.** 280,000+ active traders in Season 3 (May 25). [S032] 1.17M unique consumers (API plus retail) in the last 30 days (June 15). [S076]
- **Record.** April monthly users 71,203 vs Polymarket 678,342 (Dune via Bitcoin.com). [S132] 39,000 monthly active traders in late 2025. [S165] CoinMarketCap's AI page now says "tens of thousands" of users. [S163]
- **Gap.** 1.17M in 30 days is about 16x April's monthly users; "consumers" is undefined.
- **Strength.** Medium.
- **Caveats.** API "consumers" could count integrators' end users.

### D. LMTS token

#### C15. TGE, October 2025
- **Claim.** CJ: team tokens locked 12 months then vesting over 24; 0xBF31 is the liquidity wallet running an on-chain market-making strategy on Aerodrome; a $1.2M early cash-out was a Banana Gun sniper, not the team; 0xBF31 funds would buy back LMTS. [S085, S138, S143]
- **Record.** Stealth TGE announced around 7:30 PM UTC+8 on 2025-10-22, 13.16% circulating at launch. [S140] Wallet 0x3c58 received 40M LMTS from the ecosystem incentive allocation (outside the 25% team share); BlockBeats asks why these tokens had no lock-up. [S140, S142] Odaily: 5M moved to 0xBF31. [S140] 0x3c58 now holds 34,375,000, i.e. 5.625M less than it received. [S020] Lookonchain: 0xBF31 sold 5.63M LMTS at $0.42 average (about $2.38M) and bought back 484,748 at $0.34 (about $166K). [S141] Cryptopolitan: 0xBF31 locked in about $1M of net gains, later bought back about $461K; first-day fall of over 58%. [S138] Odaily: about $2.3M "cumulative profit" and about 10M more LMTS moved to 0xBF31. [S140] Invezz: open about $0.35, peak about $0.72, low about $0.2164; Wintermute's founder questioned the market-making explanation. [S139] Token page today: 0x3c58 still holds 34,375,000. [S020]
- **Gap.** A company-controlled liquidity wallet sold into launch demand; the company calls it market making.
- **Strength.** Medium (on-chain figures via relays; measures differ).
- **Caveats.** Do not merge sale proceeds ($2.38M, Lookonchain), "profit" ($2.3M, Odaily) and "net gains" ($1M, Cryptopolitan). The 10M transfer did not come from 0x3c58 or was returned. A third party's recollection of market-making "shenanigans" with team wallets (S199, credibility D) is not evidence and is not tied to the TGE. Verify on BaseScan (open item 8).

#### C16. Tokenomics disclosures
- **Claim.** October 2025 tokenomics: Investors 25%, Team 25%, Ecosystem 24.37%, Treasury 13%, Liquidity 10%, Kaito 1.37%, Echo 1.26%. [S175]
- **Record.** Official token page now: Investors 26.26%, Team 25%, Ecosystem 23.31%, Treasury 13%, Strategy 10%, Public Sale 1.37%, Advisers 1%, Public Allocation 0.06%. [S020] Circulating supply shown: 451,556,174, which equals 1B minus Sablier Lockup 1, Ecosystem Wallet and Investors Multisig, so Sablier Lockup 2 (254.1M) is counted as circulating; CoinGecko and Tokenomist use 131.6M. [S020, S104, S107, A07] Whitepaper has no allocation or vesting details. [S021] The page's top-10 holder table adds up to about 92.7% of supply (the seven wallets listed in section 2 total about 87.5%). [S020]
- **Gap.** Allocation table changed with no notice found (A06); official circulating supply is about 3.4x the trackers' figure.
- **Strength.** High for the numbers; the mapping between versions is inference (A06).

#### C17. Vesting and unlocks
- **Claim.** Team: 12-month hard lock plus 24-month "soft lock"; investors and Echo: 6-month lock then 24-month linear; Kaito: 50% at TGE, 50% at 6 months. [S175] CJ: team locked 12 months then vests over 24. [S085]
- **Record.** About 85.37M LMTS unlocked on 2026-04-22, almost 65% of then-released supply. [S109] Foresight: the Echo round vested 50% at TGE and 50% at 6 months, contradicting the official terms. [S165] CoinGecko's widget: next event 2026-10-22 of about 96M, including 83.33M team (one third of the 250M team allocation), 8.33M investors, 4.33M treasury; Tokenomist names only the Echo round for that date. [S104, S107] CJ, 2026-07-21: heavy sell pressure after unlocks, plan to follow. [S077]
- **Gap.** A one-third team lump at month 12 fits a 1-year cliff with 3-year vesting, not "12 months locked then 24 months of vesting" as a plain reading; aggregator models also show a lump at month 6 for investors and treasury. "Soft lock" is undefined.
- **Strength.** Medium (aggregator models conflict).
- **Caveats.** The Sablier streams decide (open item 6).

#### C18. The promised LMTS plan
- **Claim.** CJ, 2026-07-21: publishing next steps and a clear plan for LMTS. [S077] July Huddle (2026-07-31): the next three months focus on expanding where LMTS trades, deepening utility and clarifying how the token connects to the company. [S002]
- **Record.** August Huddle (2026-09-01): no token update. [S003] No plan found on the blog or X as of 2026-09-28. The Korea interview (2026-09-23) has no token content. [S171] Limitless's "rumors of being washed" post (slang). [S053] LMTS at an all-time low. [S106]
- **Gap.** Two of the three months have passed without a public deliverable.
- **Strength.** Medium (window runs to about the end of October).

#### C19. Binance dispute and a market on its own listing
- **Claim.** CJ (2025-10-14) published Binance's alleged listing asks; later: Limitless will never be a Binance puppet. [S084, S067]
- **Record.** Asks totalled about 8% of supply (1% day-one airdrop, 3% further airdrops, 1% marketing, 3% HODLer program) plus a $250K deposit and $2M of BNB collateral (BitPinas); Bankless says "a combined 9%" and adds $200K of market-maker incentives and a $1M+ PancakeSwap TVL requirement, CZ calling CJ a clout chaser, and CJ saying he signed no NDA. [S148, S146] Binance called the claims false and defamatory, said confidential talks were disclosed, said it charges no listing fees, and threatened legal action (CoinCentral only). [S147] Binance's response post was later deleted. [S148] Limitless ran its own market on whether Binance would list LMTS in 2025: resolved NO, $85,574 volume. [S027]
- **Gap.** The operator ran a market on its own token's listing (created about Oct 16, after the dispute went public), where insiders could hold non-public information.
- **Strength.** High for facts; the conflict is a question, not a finding.
- **Caveats.** No public rule on insider participation in such markets was found (open item 18b).

#### C20. Sale, listings and price
- **Claim.** Kaito sale massively oversubscribed; Coinbase listing; lowest FDV/revenue. [S153, S154, S149, S125, S062]
- **Record.** Kaito sale: $1M at $75M FDV ($0.075), about $200.97M committed, average allocation 31 USDC, median 10 USDC; participants 32,186 per Kaito's figures (32,686 per Blockchainreporter). [S154, S153] Price about $0.043 (ROI about 0.57x on the sale), about 91% below CryptoRank's ATH ($0.4753); other ATHs $0.6943 (CoinGecko), $0.7175 (CMC). [S104 to S106] Coinbase Ventures is an investor in the project Coinbase listed. [S170] Monolith: ATH FDV about $800M, a 230% premium to estimated fair value, traction mostly from airdrop farming. [S169] CertiK score 4.1/10. [S105]
- **Strength.** High.

### E. Programs, payouts and allegations

#### C21. World Cup campaign ("$1M")
- **Claim.** "Giving away $1,000,000" with an "up to" 1M USDC pool (June 13); "$1M trading competition" (June 18); "the $1,000,000 pool", 20% to random traders and 80% to the top 1,000 (June 24); "$1M World Cup challenge" (June 26, June Huddle, "18 reasons"). [S056, S188, S189, S045, S001, S187, S043] Separate UEFA predictor game with a $5,000 pool (July 2). [S190]
- **Record.** Rules PDF: pool starts at 100,000 USDC and grows with the number of Traders (anyone with one $10+ trade) to at most 1,000,000 USDC, recalculated daily; ends 2026-07-19 22:00 London; "payouts are completed by 3 August 2026"; Limitless may void XP and rewards for coordinated, artificial or abusive activity and may change the rules during the campaign. [S203] An airdrop site described the same 100K-to-1M scaling in June, with no payout date or bot rules. [S157] 2026-08-03 22:29 UTC: Limitless says it recalculated final standings, adjusted results of users who abused the system, and payouts have started rolling out. [S191] 2026-08-04 onward: allegations that the leaderboard changed overnight without notice and top users vanished. The new #1, 0x4f9679f19ea4aaa92532ed55669efdbd269e48eb, is labeled by the thread's author as an ambassador's wallet ($360K+ tournament volume); 0x2503B72C94aa9966FeF7Df1dd5555a6b9300A087, top 5 for most of the campaign, fell to #21 with about 30M XP removed despite what the author calls a similar buy/sell pattern. Also: one user's XP cut to zero, "scam" posts, and on Aug 13 still no payout for at least one user. [S192, S193, S118, S119, S121, S194] July Huddle: World Cup about 10% of volume, nothing on payouts; August Huddle: nothing. [S002, S003] No winners post; campaign pages removed. [S028]
- **Gap.** Marketed as $1M; the rules made $1M a ceiling; the final pool, number of Traders and number of voided accounts were never published; payouts were not completed by the rules' own deadline per the company's post.
- **Strength.** High for marketing vs rules and deadline. Selective-enforcement allegations are D-grade but testable on-chain (open item 15).
- **Caveats.** Voiding XP for abuse was within the rules. Many complainants look like campaign farmers; one said his stake was about $20. [S121]

#### C22. Referral and partner payouts
- **Claim.** Earn up to 40% of referred fees in USDC; 72-hour doubling for Starter (10% to 20%); top 10 referrers earned $30K in 3 weeks and $45K in a month; $120K of referral rewards in August; partners and creators earned $200K+. [S048, S049, S197, S196]
- **Record.** 32% needs $1M and 40% needs $5M of the referrer's own CLOB maker plus taker volume. [S019] Referral shares and creator fees come out of fees before the maker rebate pool. [S012] August gross fees about $0.57M, so $120K would be about a fifth. [S101] No disclosure rule for referrers or ambassadors promoting on X. [S019, S195]
- **Gap.** "Up to 40%" depends on very high own volume, which self-matching can supply (A02).
- **Strength.** Medium.

#### C23. Points and airdrops
- **Claim.** Points convert into airdrop share (Seasons 1 to 4); Season 3 airdrop 3% of supply (30M LMTS, 13M claimed in 3 hours); Season 4 runs to Oct 26 with a $200 minimum. [S005 to S007, S004, S034, S069, S198]
- **Record.** No season stated a pool size or conversion formula in advance. [S004 to S007] Season 2 about 2% of supply per a third party. [S123] Season 4 end date: body Oct 26, meta description Sep 25; X countdown implies about Oct 26; one post calls it Season 3. [S004, S198] Monthly resets. [S050] Season 4 rules posted 18 days after the season began. [S004] Wallchain multiplier complaint. [S124] The Season 3 airdrop went out May 27, before the June 30 disclosure; the report says points were cut but not whether flagged wallets claimed tokens. [S001]
- **Strength.** Medium.

#### C24. Resolution and refunds
- **Claim.** "Instant resolutions". [S043]
- **Record.** Event markets are resolved manually by the team, typically within 24 to 72 hours, with no formal dispute window. [S018] On misresolution, holders of the true winning side get only their cost basis while wrongly paid holders keep their payout. [S017] ToS: oracle outcomes are final; funds can be forfeited on reasonable suspicion. [S014]
- **Strength.** High (context on operator discretion).

#### C25. The "$21,000" allegation
- **Allegation.** A CoinLaunch commenter (ScorerFi) says Limitless "stole $21,000" from him in December 2024, unresolved. [S158, S122]
- **Record.** No market, wallet or transaction named; no corroboration; no Limitless response found.
- **Strength.** Low (E). Lead only.

#### C26. Critics' broader allegations
- **Allegations.** TheNotoriousSKi: most volume fraudulent, fake metrics, positive voices paid (2025); wash trading to mislead investors, over 90% from one wash farm, spoofed orders farming rewards, failed small orders, questions about investor diligence (May 2026). [S115 to S117, S110, S111, S113, S114, S200, S201] Lauris: recalls market-making "shenanigans" with team wallets. [S199, S068]
- **Record.** The AMM flash-loan mechanism was later confirmed by Limitless (C04). Company involvement, the 90% share, spoofing and paid praise are not corroborated.
- **Strength.** Mixed: mechanism confirmed; the rest D-grade.
- **Caveats.** Long-running personal conflict between SKi and CJ; abusive language in some posts.

### F. Corporate, legal and regulatory

#### C27. Who operates what
- **Record.** Terms and Privacy Policy name Street Chow Inc. (Panama) as operator; the Terms mention no Limitless Labs, Limitless Markets US, CFTC, market makers, points or LMTS, and have no version history. [S014, S015] Limitless Markets US is a Delaware LLC wholly owned by Limitless Labs (Cayman), signed by Hetherington as CEO of Limitless Labs. [S091] Form DCM: principal office c/o Limitless Labs in Cayman, no physical US office. [S092] limitless.network: New York, Tokyo, Seoul; describes Limitless Markets US as an exchange in New York. [S023] Rulebook naming inconsistency. [S094] Third-party profiles disagree on HQ and founding year. [S178]
- **Gap.** No public document explains the relationship between Street Chow Inc. and Limitless Labs.
- **Strength.** High (documents); the link is open (item 9).

#### C28. US access
- **Record.** Terms bar US persons from trading (browsing allowed). [S014] CJ: not launched for US customers. [S134] Casino.org (May 5) said the platform was available within the US and that it accessed 5-minute BTC contracts; republished by Public Gaming. [S136, S137]
- **Strength.** Low-medium: browsing vs trading unclear.

#### C29. Jurisdiction blocks
- **Record.** Current Terms (Sep 15): full block for Russia, Belarus, Cuba, Iran, North Korea, Syria, Crimea, Donetsk, Luhansk; trading barred for the US, "Republic of China", Ontario and Alberta. [S014] A June 19 version read by a reviewer had US and Republic of China and did not mention Canada. [S161]
- **Strength.** Medium (Canadian provinces added between June 19 and September 15; no changelog).

#### C30. CFTC application
- **Claim.** CRO hired "as it pursues DCM status"; DC trip with CRO and CCO; a disclosed partner post says the application was deemed materially complete on May 1. [S044, S082, S164]
- **Record.** CFTC portal: status Pending, dated 2026-05-01, eight public documents, no amendments, deficiency letters or comment period posted. [S090] Nothing public confirms "materially complete".
- **Strength.** High.
- **Caveats.** Most CFTC review steps are non-public. Form DCM checkbox reading is ambiguous (open item 11).

#### C31. Regulatory warnings
- **Record.** No warning found. AMF France blacklists: no entry in five of six lists; the long "other categories" list was only partly readable. [S177] Other regulators not checked.
- **Strength.** Partial negative result.

### G. Funding, promotion and partnerships

#### C32. Funding
- **Claim.** $3M pre-seed, $4M round ($7M total), $10M seed; careers page shows $10M seed; CJ: raised far less than rivals. [S151, S150, S174, S149, S026, S064]
- **Record.** About $17M in private rounds plus the $1M Kaito sale; third parties show $18M, $7M, $14M or $17M. [S159, S178] Variant, Paradigm and 1kx appear only in third-party content (X05). The July "thanks Base and Coinbase Ventures" post is ecosystem promotion, not new funding. [S081]
- **Strength.** High.

#### C33. Paid promotion and disclosure
- **Record.** Token page: LMTS can be earned by promoting Limitless on X. [S020] Kaito sale prioritized "Top Yaps" accounts. [S153] Ambassador program with rewards, higher revenue share and a direct line to the team; aimed at five groups including active X supporters. [S195, S156] Partners program: partners and creators earned $200K+. [S196] Referral payouts. [S197] A bullish Substack deep dive is disclosed partner content using project-supplied figures. [S164] No disclosure rule found for ambassadors or referrers. [S019, S195] A critic says positive voices are paid. [S117]
- **Gap.** Material paid promotion runs through several programs; disclosure practice beyond the Substack piece is unclear.
- **Strength.** Medium-high.

#### C34. Partnerships and announcements
- **Record.** NAVI and Seedorf deals with no terms. [S041, S024] Chainlink Data Streams for about 19,000 short-term markets per week; outlets disagree on whether it replaced Pyth. [S042, S168, S160] Noma and Predictefy integrations. [S054, S055] ParlayX: institutional access partnership; ParlayX is a $1.25M pre-seed startup that connects to several venues. [S052, S172, S173] Circle event in Seoul; EastPoint Seoul; Korea institution-only proposal. [S078, S002, S171] A prohibited-markets policy (assassination, harm, terrorism) announced without a policy page. [S001]
- **Relevance.** Most announcements cluster in the same weeks as the metrics push (A08).
- **Strength.** Low (context).

---

## 5. Exclusions (keep out of the piece)

- **X01.** The Arbitrum DAO 75,000 ARB grant ban (September 2026) concerns **Limitless Finance** (limitlessfi.xyz, @LimitlessFi_, founder Jeong Park, margin trading on Uniswap V3), not limitless.exchange. OpCo announced the bans approved on 2026-09-21. CoinMarketCap's AI page wrongly attributes it to LMTS. [S180 to S183, S162]
- **X02.** "Limitless Labs raises $20M Series A" (June 2026) is the Tel Aviv physical-AI and CNC company (formerly LimitlessCNC). Preqin merges the two profiles. [S185, S184]
- **X03.** Tracxn's $34.3M "Limitless" profile is a different company (appears to be Limitless AI). [S186]
- **X04.** @cjhetherington is not CJ; the CEO is @cjhtech. PredictionTalk lists the wrong handle. [S160]
- **X05.** Variant Fund, Paradigm and 1kx are named as backers only by third parties. [S133, S120]
- **X06.** "Rumors of being washed are exaggerated" (2026-08-12) is slang for being past one's prime, not an admission. [S053]
- **X07.** Paradigm's research on double counting is about Polymarket; cite for method only. [S167]

---

## 6. Analysis notes (our inference; label as such if used)

- **A01. Notional math.** Notional counts outcome shares; USDC volume counts dollars; notional divided by USDC equals one over the average price. For the week of May 4, primo_data's figures were $600M notional and $44M taker USDC [S112]; DefiLlama adjusted were $41.7M and $19.0M [S101]. The removed activity is therefore roughly $558M notional on $25M USDC, about 22x, an average price near $0.045. Trading at low prices maximises notional per fee dollar because fees are charged on USDC. Sources count differently, so treat this as an order of magnitude. In the report's example cycle, the actor buys for $9,999 and sells for $9,919 (fees 39.996 and 39.836 USDC) and recovers 79.82 USDC as LP, so the only costs are gas and slippage. [S001]
- **A02. Self-matching under 100% rebates.** A taker fee on a matched trade goes into the market's rebate pool, shared pro-rata among makers. A party that is the dominant maker in a market and also takes against its own orders from another wallet gets back most of the fee. Self-trade prevention does not stop this across profiles. [S012, S016] The same volume raises points, referral tiers and public volume. Net cost: gas, spread paid to others, the share of fees going to other makers, and any referral or creator share taken first. Whether one can refer one's own wallets is not stated (open item 18).
- **A03. Fee pass-through.** Rebates of $9.2M in four months [S051] vs DefiLlama gross fees of $9.30M for April to July [S101]: about 99%. After DefiLlama split payouts out, payouts were 89% of fees. [S101] "Annualized revenue" therefore describes annualized pass-through.
- **A04. The April 25 step change.** Adjusted daily USDC volume: $1.67M (Apr 24), $10.5M (Apr 25), $17.7M (Apr 26). [S101] Weekly notional/USDC fell from about 5x (January to mid-April) to 2.5x (week of Apr 20) and 1.6x (Apr 27). This is activity the flash-loan filter did not remove: the order book, or AMM wallets not on the list. It came 11 days after 100% rebates (Apr 14), 3 days after the 85.37M unlock (Apr 22) and 3 days before DefiLlama began counting AMM fees (Apr 28). Tested in a06 and a16: the step is the 9Ns5 cluster.
- **A05. Were fees inflated?** Flash-loan AMM fees went to the LP, i.e. the actor, yet DefiLlama counted AMM fees as protocol revenue from 2026-04-28 until the 2026-07-05 filter. [S202] At 0.40% on about $25M a week of removed USDC volume (A01), that is on the order of $100K of fees a week. Separately, if order-book self-matching was large, the fees were circular. Test: USDC flows into the fee recipient and out of the rewards distributor, by wallet cluster.
- **A06. Tokenomics mapping.** October 2025 to now: Investors 25% to 26.26% (+1.26, the size of the Echo round, which disappears); Ecosystem 24.37% to 23.31% (-1.06, the size of the new Advisers 1% plus Public Allocation 0.06%); Liquidity 10% becomes Strategy 10%; Kaito 1.37% becomes Public Sale 1.37%. Both tables sum to 100%.
- **A07. Circulating supply arithmetic.** 1,000,000,000 minus 380,566,867 (Lockup 1) minus 161,642,086 (Ecosystem) minus 6,234,872 (Investors Multisig) equals 451,556,175, one token from the page's 451,556,174. Lockup 2's 254,099,824 is therefore treated as circulating.
- **A08. The window.** Apr 1: flash-loan window opens. Apr 14: 100% rebates. Apr 22: unlock. Apr 25: step change. May 1: CFTC filing and April record claims. May 21: MM survey and 13x question. May 25: Season 3 ends at "$4B", CJ vs critics. May 27: airdrop. Weeks of May 25 and Jun 1: peak adjusted notional (355.6M, 253.1M). Jun 1: window closes. Jun 4 to 16: revenue, rebate, user and partnership claims. About Jun 17: Bernstein call coverage. Jun 30: disclosure. Jul 5: DefiLlama filter. Then adjusted USDC volume falls: June $173.0M, July $85.9M, August $27.5M, September to the 27th $10.6M. [S101]

---


---

## 7. Open items

1. Whether the flash-loan wallets (309 in the report, 328 on DefiLlama) claimed Season 3 airdrop tokens: find the claim contract from the May 27 claims, check transfers to the 328 addresses.
2. Pull `dune.limitless_exchange.dataset_flashloan_daily_volume` and `dataset_flashloan_wallets`: daily volume, first and last dates, wallet count.
3. Overlap between the 328 flash-loan addresses and the a06 cluster wallets (done: none).
4. Reconcile 309 (Notion list, report) vs 328 (DefiLlama list).
5. Attribute the 2026-04-25 step change (A04).
6. Sablier Lockup 1 and 2 stream parameters (start, cliff, end, recipients) against the stated vesting (C17).
7. Any LMTS buybacks after December 2025: LMTS inflows to 0xBF31, treasury and multisigs.
8. BaseScan check of TGE flows: 0x3c58 to 0xBF31 transfers, 0xBF31 sells and buybacks on 2025-10-22/23.
9. Street Chow Inc. in the Panama public registry: directors and any link to Limitless Labs.
10. Rule 5.17 full text (Exhibit M, from p. 53).
11. Form DCM application vs amendment checkbox (visual check).
12. Bernstein call date and source of the "close to $2B" figure.
13. Date the BTC/ETH 5m/15m rebate fell from 100% to 30%.
14. When Ontario and Alberta were added to the Terms (Wayback snapshots of the ToS page).
15. World Cup: final pool size, number of Traders, number of voided accounts, payout transactions, and the trading patterns of the wallets named in S192.
16. Whether DefiLlama displayed the inflated figures before 2026-07-05 (Wayback snapshots of defillama.com/protocol/limitless-exchange in May and June).
17. Data source behind "top 5 fee generator on Base" and "top 20 by monthly earnings" (DefiLlama or Token Terminal).
18. Whether referral rules allow referring your own wallets. 18b: any rule on insiders trading markets about Limitless itself (S027).
19. Full text search of the AMF "other categories" list; warning lists of other regulators.
20. The ScorerFi post (S122) and any Limitless reply.
21. End of October: whether the promised LMTS plan appears (C18).
22. Chinese original of the Odaily TGE article (timing of contract creation).

---

## 8. Verification playbook

**Load the ledger**
```python
import json
recs = [json.loads(l) for l in open("limitless_evidence.jsonl", encoding="utf-8")]
by_id = {r["id"]: r for r in recs}
def for_claim(cid): return [r for r in recs if cid in r["claims"]]
for r in for_claim("C21"): print(r["id"], r["credibility"], r["url"])
```

**DefiLlama**
- Daily series: `https://api.llama.fi/summary/dexs/limitless-exchange?dataType=dailyNotionalVolume`, `...?dataType=dailyVolume`, `https://api.llama.fi/summary/fees/limitless-exchange?dataType=dailyFees`, `...?dataType=dailyRevenue`. Each returns `totalDataChart` as `[timestamp, value]` pairs; sum by UTC month and compare with S101.
- Adapter history: `git clone --filter=blob:none https://github.com/DefiLlama/dimension-adapters && git -C dimension-adapters log --date=iso --format='%h %ad %an | %s' -- dexs/limitless-exchange/`. Key commits: `424330eda16e8ef76e9a44babd0a2b5b2edcbcc5` (Apr 2), `9323a9440a8cff4f356b6ee766f207573e755364` (Apr 28), `800642222b334b2f8fbaed0211e08025b4e9b0e0` (Jul 5), `6c61fd80d2cc55f4683e26124a7617ee91194805` (Aug 10). PR pages: /pull/5764, /pull/6576, /pull/7969, /pull/8676.
- Flash-loan list: fetch `flashloan-wallets.ts`, extract `0x` addresses (expect 328), intersect with the a06 cluster wallets.

**On-chain (Base)**
- Transactions: `https://basescan.org/tx/0xe19542e6b7f50638eea02c43eca08f888f0e3b8848f55af727f92243caed443c`, `https://basescan.org/tx/0x02e71256253919dbb522ec8cc6aefa003b5223efeb4e2b2087c1e6df82f40eee`.
- Fee and rebate flows: USDC transfers into `0x88eaf31f9fE392002e0E818527f8259af92287b1` (fee recipient) and out of `0xE895CaE6B705d584b03cd82Fdd57cf7F8c52FaDB` (rewards distributor), grouped by recipient cluster.
- Token: LMTS transfers for `0x3c583Be4...`, `0xBF313297...`, Sablier lockups `0xe261B366...` and `0xc19a09A6...`.
- Order-book trades: `OrderFilled` events on the CTF and neg-risk exchanges listed in section 2.

**Dune**
- `select * from dune.limitless_exchange.dataset_flashloan_daily_volume order by 1`
- `select count(*) from dune.limitless_exchange.dataset_flashloan_wallets`

**Documents**
- CFTC PDFs: download S091 to S094 plus Exhibits G-2 and G-3 (URLs in S091 key_facts), run `pdftotext -layout`, search "5.17", "2.12", "wash".
- Limitless pages: re-fetch S001, S013, S014, S020, S203 before publication; they change.

**X posts**
- Need a logged-in browser. Filter `recs` where `url` contains `x.com`; re-read before quoting and archive each (archive.org or screenshots).

---

## 9. Verification status (2026-09-28)

- Four independent re-checks, by reviewers who had not seen the drafting, covered S001 to S028, S090 to S109, S130 to S155 and S156 to S186. Corrections applied to the ledger include: referral tier thresholds (S019), rules PDF now readable (S028, S203), Chainlink TWAP date removed (S018), top-holder share 92.7% (S020), exhibit citations for the Cayman parent and signatory (S091), unlock and ATL figures (S104, S106, S107), TGE proceeds vs profit wording (S138 to S142), Binance details moved to the right outlet (S146, S148), Kaito participant count (S153), "stole $21,000" wording (S122, S158), partner disclosure on the Substack piece (S164), Arbitrum multisig history (S181), AMF check scope (S177).
- DefiLlama monthly figures (S101) were recomputed from the saved API pulls and match; the API itself was not reachable on 2026-09-28.
- DefiLlama adapter code and commit history (S102, S202) were read from a clone of the public repository.
- Not re-reachable on 2026-09-28: S172 (HTTP 429), S186 (robots). Snippet-only: S084, S085, S123, S124, S125, S175 copies, S176, S179.
- X posts were read directly in a logged-in browser on 2026-09-27 and 2026-09-28; the second pass added S187 to S201 and the World Cup, primo_data, Lauris and TheNotoriousSKi post IDs.
