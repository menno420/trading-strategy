# Broker & exchange landscape for a small-account custom bot (NL, 2026-07-12)

> **Status:** `research` — desk research only, RESEARCH-ONLY lane. Ranked,
> cited landscape of NL-legal places to run a personal trading bot on a
> €100–200 account. No accounts were created, no trades placed, no backtests
> run. This doc identifies the cheapest place to run a bot; it is **not**
> evidence that a profitable bot exists. General information, **not legal or
> financial advice.**

| Field | Value |
|---|---|
| Owner use case | NL resident · €100–200 start · custom bot via API · one open trade at a time |
| Research date / all citations accessed | 2026-07-12 |
| Sources | 4 broker/exchange clusters (IBKR·LYNX·MEXEM / Saxo·T212·DEGIRO / Alpaca·CFD / Bitvavo·Kraken) + NL crypto-legality desk research |
| #1 pick | **Bitvavo** — NL-domiciled MiCA CASP, ~0.50% round-trip, no per-order minimum |
| Runner-up | **MEXEM** — regulated real equities, ~2.0% round-trip at €100 |
| Fee-reality verdict | At €100 the per-order **minimum commission** kills stock brokers; crypto wins because fees are pure % with **no minimum** |
| Activation status | FLAG-ONLY. Going live needs an explicit owner order lifting the RESEARCH-ONLY rail. No agent self-activates. |

---

## 1. TL;DR / Recommendation

- **#1 — Bitvavo (crypto spot).** NL-domiciled, MiCA CASP licensed via the AFM,
  ~€5 minimum order, **0.50% round-trip at €100** (0.25% taker each side / 0.15%
  maker), free SEPA/iDEAL, REST + WebSocket API, personal bots explicitly
  allowed, and — decisively — **no per-order minimum commission.** Lowest
  friction at this account size. (No confirmed public spot sandbox — see §4.)
- **Runner-up — MEXEM (regulated real equities).** If the owner wants real
  Euronext-Amsterdam equities rather than crypto: IBKR introducing broker,
  assets custodied at Interactive Brokers Ireland (IBIE, Central Bank of
  Ireland), **~2.0% round-trip** on a €100 EUR instrument, €0 minimum deposit,
  full IBKR API (TWS + Client Portal REST + FIX), paper trading via IBKR.
- **Fee reality (one line):** at €100 a bot pays for *access*, not for *size* —
  fixed per-order commission floors (IBKR ~€1/side, Saxo ~€1–2/side) dominate
  the percentage rate, and crypto only wins because it charges a pure percentage
  with no floor. Even Bitvavo's 0.50% round-trip bleeds capital for a bot with
  no real edge.

---

## 2. Owner's use case

- **Who:** a single Netherlands resident, trading **only their own money**.
- **Size:** start with **€100–200**.
- **How:** a **custom bot via API**, **one open trade at a time** to begin with;
  later, possibly multiple bots running different position-sizing schemes.
- **Constraint:** this is **research only**. Agents activate nothing — no
  account is opened, no key is generated, no order is sent by any agent. Every
  activation is an owner decision (see §7).

---

## 3. NL legality

**Boundary:** trading your **own** money with your **own** bot needs **no AFM
licence** (own-account dealing is exempt). Managing **other people's** money —
pooling funds, or offering your bot/signals as an investment service to third
parties — makes you a *beleggingsonderneming* / portfolio manager and **does**
require an AFM (MiFID investment-firm) licence.

- An "investment firm" (*beleggingsonderneming*) under the **Wft** (Wet op het
  financieel toezicht) is a party that *provides an investment service or
  performs an investment activity for/to third parties*; such firms must be
  **AFM-licensed** (with DNB prudential advice).
  [AFM — beleggingsondernemingen](https://www.afm.nl/en/sector/beleggingsondernemingen)
  (accessed 2026-07-12);
  [AFM — vereisten en vergunningen](https://www.afm.nl/nl-nl/sector/beleggingsondernemingen/vereisten-en-vergunningen)
  (accessed 2026-07-12).
- **Trading purely for your own account is treated differently.** Under the
  **Vrijstellingsregeling Wft**, dealing on own account is **exempt** from the
  NL licensing regime — buying/selling for yourself via your own API keys is
  not "an investment service provided to another person," so it triggers no
  AFM investment-firm licence obligation. Spot crypto additionally sits under
  **MiCA**, not MiFID II, and MiCA CASP licensing falls on the *exchange*
  (Bitvavo/Kraken), not on a retail customer trading their own funds.
  [AFM — MiFID II licence-obligated parties](https://www.afm.nl/en/sector/themas/belangrijke-europese-wet--en-regelgeving/mifid-ii/vergunningen/vergunningplichtigen)
  (accessed 2026-07-12).
  > **UNVERIFIED (source-flagged):** the specific **Wft article** for the
  > own-account-dealing exemption (Art. 10a of the Vrijstellingsregeling Wft was
  > referenced) could **not** be confirmed against the consolidated legal text.
  > The exemption *principle* is confirmed by the AFM sources above; the exact
  > article number is UNVERIFIED.
  > [AFM — uitleg vergunningen/vrijstellingen (PDF)](https://www.afm.nl/~/media/files/registers/uitleg-vergunningen-vrijstellingen-beleggingsondernemingen.ashx)
  > (accessed 2026-07-12).
- **The line you must not cross:** the moment you manage or trade money for
  other people, pool their funds, or offer your bot/signals as an investment
  service, you need an AFM licence.
  [AFM — vereisten en vergunningen](https://www.afm.nl/nl-nl/sector/beleggingsondernemingen/vereisten-en-vergunningen)
  (accessed 2026-07-12).

**Plain-language takeaway:** a single NL resident running a personal bot on a
€100–200 account, trading only their own money, needs **no AFM licence**. This
is general information, **not legal advice.**

---

## 4. Ranked landscape

Best-fit first. Round-trip = buy + sell of one position; percentages are of the
€100 position value. "EU stock" = EUR-denominated Euronext-Amsterdam instrument
(avoids FX minimums). All figures accessed 2026-07-12; broker schedules change
without notice.

| # | Broker | Regulator / entity (NL-legal?) | Bot/API allowed (ToS) | Min deposit | Min trade/order | Round-trip % at €100 | API type | Sandbox/paper? | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Bitvavo** | Bitvavo B.V. — MiCA CASP via **AFM (NL)** ✓ | **Yes** — personal bots, own keys | ~€0 (free SEPA/iDEAL) | ~€5 order | **0.50%** (maker 0.30%) | REST + WebSocket | **No confirmed public spot sandbox** | **PICK.** Lowest friction; pure %, no per-order floor |
| 2 | **MEXEM** | MEXEM Ltd — CySEC 325/17; custody at **IBIE / CBI** ✓ (AFM/FSMA notified) | **Yes** | €0 | €1 min/order (EU stock) | **~2.0%** | TWS API, Client Portal REST, FIX | Paper via IBKR (direct provisioning UNVERIFIED) | **Runner-up** for real equities. Avoid US/USD (FX min dominates) |
| 3 | **IBKR direct (IBIE)** | Interactive Brokers Ireland Ltd — **CBI** ✓ (passported to NL) | **Yes** | €0 | €1.25 min/order (EU stock, Tiered) | **~2.5%** | TWS API, Client Portal REST, FIX | **Yes** (IBKR paper) | Solid alt to MEXEM; best-documented API + paper |
| 4 | **Trading 212** | T212 EU GmbH (BaFin) / Markets Ltd (CySEC) ✓ (confirm entity at signup) | **Partial** — first-party Public API (Beta), live orders only | €1 | €0 comm (EUR ETF) | **~0%** (+ spread) / ~0.30% FX on US | REST (Beta) | **No** API sandbox | Cheapest, but Beta + automation ToS only PARTIALLY VERIFIED |
| 5 | **Kraken** | Payward Europe/Ireland — MiCA CASP via **CBI** ✓ | **Yes** | ~€0 | ~€5 / 0.0001 BTC | **1.60%** (Tier 1, maker 0.80%) | REST + WebSocket + FIX | Futures demo only; **no spot sandbox** | Works, but ~3× Bitvavo after the July-2026 fee change |
| 6 | **Saxo (OpenAPI)** | Saxo Bank A/S — Danish FSA + NL branch DNB/AFM ✓ | **Yes** — retail personal use explicit | €0 | ~€2 EU / $1 US min/order | **~4.0%** EU stock / ~2.3% US | REST + streaming (WebSocket/SignalR) | **Yes** — full SIM sandbox ($100k) | Best sandbox, worst small-size economics among banks |
| — | **Coinbase Advanced** | MiCA CASP (EU) ✓ | Yes | ~€0 | ~€1–5 (UNVERIFIED) | **~1.20%** (UNVERIFIED, secondary source) | REST + WebSocket + FIX | — | Noted only |
| ✗ | **DEGIRO (flatexDEGIRO)** | flatexDEGIRO Bank AG/SE — BaFin + NL branch DNB/AFM ✓ | **NO** — no official API; automation unsupported | €0 | per-order fixed fees | ~4.5% US / 6–10% EU / ~1–2% Core ETF | **None** (unofficial libs risk account blocking) | — | **DISQUALIFIED** — no API, automation not permitted |
| ✗ | **LYNX** | LYNX B.V. (Amsterdam) — AFM/DNB; IBKR intro ✓ | Yes | ~€3,000 (UNVERIFIED) | **€6 min/order** | **~12%** | TWS API, LYNX Gateway, FIX | Paper via IBKR | **DISQUALIFIED** — €6/order floor + €5/mo min-activity fee |
| ✗ | **Pepperstone GmbH** | BaFin 151148; EEA-passported to NL/AFM ✓ | Yes — EAs explicit | No hard min | **0.01 lot ≈ €1,000 notional** | n/a (€80–160 UNREACHABLE) | MT4/MT5, cTrader (Open API/FIX) | Free demo | **Not recommended** — leveraged CFD; ~75–77% of retail LOSE money |
| ✗ | **IC Markets EU** | CySEC 362/18; EEA-passported to NL/AFM ✓ | Yes — EAs explicit | €200 | **0.01 lot ≈ €1,000 notional** | n/a (€80–160 UNREACHABLE) | MT4/MT5, cTrader (Open API/FIX) | Free demo | **Not recommended** — leveraged CFD; ~70.6% of retail LOSE money |
| ✗ | **Alpaca** | Alpaca Securities LLC (US b-d); **no AFM passport** for retail self-serve | Yes (REST + WebSocket) | $1 | ~$1 (fractional) | ~0% comm (+ FX on funding) | REST + WebSocket | Yes (free paper) | **Excluded** — NL retail eligibility UNVERIFIED / likely unavailable |

### Per-cluster detail (with citations)

**#1 Bitvavo (Amsterdam, NL).** Bitvavo B.V. holds a **MiCA/MiCAR CASP licence
granted by the Dutch AFM**; DNB supervises the prudential/EMT side. Personal
bots with your own API keys are allowed (the API "lets you trade, manage
balances, and automate your account"); a *third party operating bots as a
service for others* additionally needs Bitvavo's Developer/API Partner
Agreement — not the personal-bot case. Entry tier (30-day volume < €100k):
**0.25% taker / 0.15% maker → 0.50% round-trip at €100** (€0.50), maker-both-
sides 0.30% (€0.30). ~€5 min order, **no per-order minimum commission**, free
SEPA/iDEAL. Native EUR pairs; reduced fees on USDC/EUR & USDT/EUR. **Sandbox:**
no public spot sandbox confirmed — expect to paper-trade via your bot's dry-run
or tiny real orders.
[Bitvavo MiCA licence](https://bitvavo.com/en/news/bitvavo-obtains-mica-licence)
(accessed 2026-07-12);
[Bitvavo — what the MiCAR licence means](https://support.bitvavo.com/hc/en-us/articles/4405243980945-What-does-Bitvavo-s-MiCAR-license-from-the-AFM-mean-for-me)
(accessed 2026-07-12);
[AFM — CASP licensing body](https://www.afm.nl/en/sector/cryptopartijen/vereisten-en-vergunningen/casp-vergunning)
(accessed 2026-07-12);
[AMF white list — Bitvavo B.V.](https://www.amf-france.org/en/warnings/white-lists/daspcasp/bitvavo-bv)
(accessed 2026-07-12);
[Bitvavo API docs](https://docs.bitvavo.com/) (accessed 2026-07-12);
[Bitvavo trading rules](https://bitvavo.com/en/trading-rules) (accessed 2026-07-12);
[Bitvavo fees](https://bitvavo.com/en/fees) (accessed 2026-07-12);
[Bitvavo — trading fee](https://support.bitvavo.com/hc/en-us/articles/4405175148689-What-is-the-trading-fee-when-I-buy-or-sell-crypto)
(accessed 2026-07-12).

**#2 MEXEM (IBKR introducing broker, Cyprus).** MEXEM Ltd, CySEC licence
**325/17**, notified into NL (AFM) and Belgium (FSMA); cash and assets custodied
at **Interactive Brokers Ireland Ltd (CBI)**. Bots allowed: Client Portal API
(REST), TWS API ("automate your trading strategies… made available to any
clients with trading access"), FIX. **No minimum deposit** to open or stay
active. EU stocks/ETFs 0.06%, **min €1/order → ~2.0% round-trip at €100**
(~1.25% at €160); no inactivity/monthly/deposit fees. **Currency conversion
0.005%, min €5/$5 per conversion — so prefer EUR instruments**; US/USD is
punishing at this size. Paper trading via the underlying IBKR platform (whether
MEXEM provisions paper accounts directly is UNVERIFIED).
[MEXEM regulation FAQ — CySEC 325/17, assets at IBIE](https://brokerchooser.com/broker-reviews/mexem-review/regulation-safety-faq)
(accessed 2026-07-12);
[MEXEM API page — REST/TWS/FIX](https://www.mexem.com/api) (accessed 2026-07-12);
[MEXEM — no minimum deposit to stay active](https://www.mexem.com/faqs/what-is-the-minimum-deposit-required-for-the-account-to-stay-active)
(accessed 2026-07-12);
[MEXEM fees — EU 0.06%/€1 min, FX 0.005% min €5/$5](https://www.mexem.com/fees)
(accessed 2026-07-12).

**#3 IBKR direct (IBIE).** EU/EEA residents contract with **Interactive Brokers
Ireland Limited**, regulated by the **Central Bank of Ireland**, passported into
NL; NL retail get **IBKR Pro only**. TWS API "a simple yet powerful interface
through which IB clients can automate their trading strategies" (plus Client
Portal REST + FIX). **No minimum deposit; no inactivity fee since July 2021.**
EU stocks Tiered 0.05%, **min €1.25/order → ~2.5% round-trip at €100** (~1.56%
at €160). US route adds an FX conversion (**min $2/conversion**) — prefer EUR
instruments. **Paper trading confirmed** via Account Management.
[Central Bank of Ireland — IBIE](https://www.centralbank.ie/docs/default-source/publications/consultation-papers/cp158/interactive-brokers-ireland-limited-response-to-cp158.pdf?sfvrsn=c4436a1a_2)
(accessed 2026-07-12);
[IBKR EU consolidation into Ireland](https://www.interactivebrokers.com/en/general/about/mediaRelations/9-29-23.php)
(accessed 2026-07-12);
[TWS API — automate trading strategies, paper trading](https://interactivebrokers.github.io/tws-api/introduction.html)
(accessed 2026-07-12);
[IBKR EU stock commissions — Tiered 0.05%/€1.25](https://www.interactivebrokers.ie/en/pricing/commissions-stocks-europe.php)
(accessed 2026-07-12, via search snippet; page returned HTTP 403 to automated fetch — exact Fixed-plan minimum UNVERIFIED);
[No inactivity fee since Jul 2021 / no minimum deposit](https://brokerchooser.com/invest-long-term/costs/inactivity-fee-interactive-brokers)
(accessed 2026-07-12).

**#4 Trading 212.** Two EEA entities — **Trading 212 EU GmbH (BaFin 10109603)**
and **Trading 212 Markets Ltd (CySEC 398/21)**; NL clients are generally
onboarded under the BaFin entity, but the exact entity per NL account is
**PARTIALLY VERIFIED — confirm at signup**. First-party **Public API (Beta)**:
generate an API Key + Secret in-app (Settings → API), permissions incl. orders,
optional IP allowlist — the sanctioned path for a self-built bot on the General
Invest account. **Order placement is documented against live accounts only; no
API sandbox.** Fees: **€0 commission** on stocks/ETFs (Invest), **~0.15% FX per
conversion** (≈0.30% round-trip on US stocks; avoidable with EUR-denominated
UCITS ETFs), plus the bid/ask spread (the real cost of "zero commission"). €1
min deposit.
> **Automation ToS = PARTIALLY VERIFIED:** no explicit "automation prohibited"
> clause found, and no explicit blanket "allowed" clause either — the existence
> of an official order-placing API key with an "orders" permission is the
> operative signal. The API is Beta and its status can change.
[CySEC register — T212 Markets Ltd](https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/89835/)
(accessed 2026-07-12);
[T212 help — API key](https://helpcentre.trading212.com/hc/en-us/articles/14584770928157-Trading-212-API-key)
(accessed 2026-07-12);
[T212 API docs](https://docs.trading212.com/api) (accessed 2026-07-12);
[brokerchooser — T212 fees](https://brokerchooser.com/broker-reviews/trading-212-review)
(accessed 2026-07-12);
[T212 help — FX fee](https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA)
(accessed 2026-07-12).

**#5 Kraken (Payward Europe/Ireland).** Serves NL via its **Ireland-authorised
MiCA CASP** (Payward Europe Solutions Ltd / Payward Ireland Ltd, **Central Bank
of Ireland**, authorised 25 June 2025), passporting across the EU/EEA. Bots
allowed (REST, WebSocket, FIX 4.4); trading rules prohibit market abuse. ~€5 min
order. **Per the July 2026 cross-platform fee-tier change, the entry tier (Tier
1, 30-day volume < $2,500) is now 0.80% taker / 0.40% maker → 1.60% round-trip
at €100** (€1.60), maker-both-sides 0.80%. **No per-order minimum, but ~3×
Bitvavo at this size.** Futures demo/sandbox exists; **no confirmed public spot
sandbox**.
> **UNVERIFIED / correction of common reviews:** the widely-quoted "0.26% taker
> / 0.16% maker" is now a *higher* volume tier (~$100k+), **not** the entry
> tier — several secondary reviews still cite the old numbers; treat those as
> outdated.
[Kraken — where licensed/regulated](https://support.kraken.com/articles/where-is-kraken-licensed-or-regulated)
(accessed 2026-07-12);
[Kraken MiCA licence (CBI)](https://blog.kraken.com/news/mica-license-central-bank-of-ireland)
(accessed 2026-07-12);
[Kraken trading API](https://www.kraken.com/features/trading-api) (accessed 2026-07-12);
[Kraken fee schedule](https://www.kraken.com/features/fee-schedule) (accessed 2026-07-12);
[Kraken — cross-platform fee-tier change (July 2026, Tier 1 0.40%/0.80%)](https://support.kraken.com/articles/cross-platform-fee-tier-changes)
(accessed 2026-07-12).

**#6 Saxo (OpenAPI).** **Saxo Bank A/S** (Danish FSA full bank) via its **NL
branch** under DNB/AFM; cash covered by the **Danish** deposit guarantee
(€100k), not the Dutch scheme. Bot/API **explicitly permitted for retail
personal use** ("Direct retail of Saxo Bank may use the OpenAPI for personal
use"); mature **REST + streaming (WebSocket/SignalR)** with a **full SIM
sandbox** (simulated $100k) — **the best sandbox in this whole landscape**. €0
min deposit. But EU stocks 0.08% with **~€2 per-order minimum** (US $1 min) plus
**0.25% FX per conversion** → **~4.0% round-trip at €100 on an EU stock** (~2.3%
on a US stock; min bites at this size). Best sandbox, worst small-size economics
among the banks.
[brokerchooser — Saxo fees](https://brokerchooser.com/broker-reviews/saxo-bank-review/saxo-bank-fees)
(accessed 2026-07-12);
[Saxo OpenAPI — personal use permitted](https://openapi.help.saxo/hc/en-us/articles/4416505486481-Can-I-use-OpenAPI-for-personal-use)
(accessed 2026-07-12);
[Saxo OpenAPI environments (SIM sandbox)](https://www.developer.saxo/openapi/learn/openapi-environments)
(accessed 2026-07-12);
[Saxo — FX conversion fee 0.25%](https://www.help.saxo/hc/en-us/articles/360001286566-What-is-the-fee-to-convert-cash-into-a-different-currency)
(accessed 2026-07-12).

**Coinbase Advanced (noted only).** Also a MiCA-route option but more expensive
at small size: entry maker/taker ~0.40% / 0.60% → **~1.20% round-trip** (€1.20
on €100). Included only for completeness.
> **UNVERIFIED** — secondary source, not confirmed against Coinbase's own
> schedule.
> [bitget academy — Kraken/Coinbase fees](https://www.bitget.com/academy/kraken-coinbase-fees)
> (accessed 2026-07-12).

**DEGIRO (DISQUALIFIED).** flatexDEGIRO Bank AG/SE (BaFin) via NL branch under
DNB/AFM. **No official API and no support for automated/bot trading**; the
consistent official-helpdesk position is "no API / no automated trading," and
unofficial reverse-engineered libraries risk **account blocking**. Per-order
fixed fees make single-stock round trips at €100 cost ~4.5% (US) to 6–10% (EU).
> **UNVERIFIED:** a verbatim anti-automation ToS clause could **not** be
> retrieved (helpdesk pages 503'd on direct fetch; client-agreement PDF not
> located) — the "no API/no automation" position is consistent across sources
> but the exact clause is NOT FOUND at source.
[DEGIRO helpdesk — automated trading/bots](https://www.degiro.com/uk/helpdesk/trading-platform/can-i-automate-trades-or-use-trading-bots-degiro)
(accessed 2026-07-12);
[brokerchooser — DEGIRO automated trading](https://brokerchooser.com/broker-reviews/degiro-review/automated-trading-systems)
(accessed 2026-07-12);
[brokerchooser — DEGIRO fees](https://brokerchooser.com/broker-reviews/degiro-review/degiro-fees)
(accessed 2026-07-12).

**LYNX (DISQUALIFIED).** LYNX B.V. (Amsterdam, AFM/DNB), an IBKR introducing
broker (assets at IBIE). Bots allowed (same IBKR stack), but the official price
list (valid 30.04.2026) sets Euronext-Amsterdam EUR at 0.06% with a **€6.00
per-order minimum → ~12% round-trip at €100** (~7.5% at €160), plus a **€5/month
min-activity fee** (waived first 3 months). The €6/order floor is fatal at this
position size.
> **UNVERIFIED:** a **~€3,000 minimum deposit** (Curvo) is not confirmed in
> LYNX's own price list — but if real it alone exceeds the €100–200 target.
[LYNX B.V. entity + AFM/DNB, assets at IBIE](https://www.lynxbroker.com/info/security/)
(accessed 2026-07-12);
[LYNX List of Prices & Services 2026 — AEB EUR 0.06% min €6.00; monthly min-activity €5](https://lynx-car-compliance-documents-production.s3.amazonaws.com/IE/archive/NL_List_of_Prices_and_Services_ENG___2026-04-30T06_01_58_982Z.pdf)
(accessed 2026-07-12);
[LYNX API examples](https://github.com/lynxbroker/API-examples) (accessed 2026-07-12);
[Curvo — LYNX minimum deposit €3,000 (UNVERIFIED)](https://curvo.eu/article/lynx-vs-interactive-brokers)
(accessed 2026-07-12).

**Pepperstone GmbH / IC Markets EU (NOT RECOMMENDED — wrong instrument class).**
Both are confirmed EU-regulated (**Pepperstone GmbH — BaFin 151148**;
**IC Markets (EU) Ltd — CySEC 362/18**), EEA-passported to NL/AFM, and EAs are
explicitly allowed (MT4/MT5, cTrader Open API/FIX, free demos). **But they are
leveraged CFD brokers**, and the smallest tradable size is **0.01 lot ≈ €1,000
notional** for EUR/USD — so the owner's **€80–160 notional is physically
UNREACHABLE**. Per-trade dealing cost is tiny in absolute terms (~$0.07–0.16
round-turn), but the instrument class is wrong for this budget and the risk is
high: retail-loss disclosures cluster around **~75–77%** (Pepperstone) and
**~70.6%** (IC Markets EU) of retail accounts LOSE money.
> **UNVERIFIED:** exact current retail-loss % varies by reporting
> period/entity; the specific AFM register line-item for each passported entity
> was not individually pulled (the passport mechanism itself is confirmed).
[Pepperstone GmbH — BaFin 151148](https://commodity.com/brokers/pepperstone-review/)
(accessed 2026-07-12);
[Pepperstone EAs supported (MT5)](https://www.metatrader5.com/en/find-broker/pepperstone)
(accessed 2026-07-12);
[IC Markets EU — CySEC, ESMA rules, EAs permitted, ~70.64% lose money](https://iamforextrader.com/en/broker/ic-markets/europe/)
(accessed 2026-07-12);
[BaFin passporting mechanism](https://www.bafin.de/EN/Aufsicht/BankenFinanzdienstleister/Passporting/Wertpapierhandelsunternehmen/wertpapierhandelsunternehmen_node_en.html)
(accessed 2026-07-12).

**Alpaca (EXCLUDED on availability).** The retail brokerage is **Alpaca
Securities LLC**, a **US** broker-dealer with an excellent REST + WebSocket API
and free paper trading — but **NL retail eligibility is UNVERIFIED / likely
unavailable**: Alpaca publishes **no country list** (only Canada is explicitly
excluded) and directs everyone to email support, and the separate "Alpaca
Europe" (April 2026) is **B2B broker-infrastructure via WealthKernel Ltd (FCA
723719), not a retail self-serve account**. There is **no EU/AFM
investor-protection passport** on the US entity. Great API where it works, but
we cannot confirm an NL resident can open a personal account.
[Alpaca — international](https://alpaca.markets/international) (accessed 2026-07-12);
[Alpaca — countries available (email support)](https://alpaca.markets/support/countries-alpaca-is-available)
(accessed 2026-07-12);
[Alpaca Europe — B2B infra launch](https://alpaca.markets/blog/alpaca-expands-into-europe-and-launches-european-equities-trading/)
(accessed 2026-07-12);
[Alpaca — connect to API (paper trading)](https://alpaca.markets/learn/connect-to-alpaca-api)
(accessed 2026-07-12).

---

## 5. Fee reality at this account size

At €100 the enemy is the **fixed per-order minimum commission**, not the
percentage rate:

- **Stock brokers charge a floor per order.** IBKR family ~€1–1.25/side, Saxo
  ~€1–2/side, LYNX €6/side, DEGIRO €1 handling + commission/side. On a €100
  position that floor becomes 2–12% round-trip — the percentage rate is
  irrelevant because the floor bites first. FX conversion minimums (IBKR
  $2/conversion, MEXEM €5/conversion, Saxo 0.25%) make USD instruments worse
  still, so an equities bot should trade **EUR-denominated Euronext-Amsterdam
  instruments**.
- **Crypto wins because fees are pure percentage with NO minimum.** A €100
  Bitvavo order costs €0.25 (taker) — cents, not a €1–6 floor. That is the
  single structural reason crypto beats stock brokers at this size.
- **CFD brokers can't even take the trade.** The 0.01-lot floor (≈€1,000
  notional) makes an €80–160 position physically impossible, regardless of how
  cheap the per-lot commission looks.
- **But cheap ≠ free.** Even Bitvavo's **0.50% round-trip** means a bot that
  trades a few times a day pays several percent of the account per week in
  costs. Without a real, cost-beating edge, that is a steady bleed.

---

## 6. Honest expectations (do NOT overstate)

Our own completed research program found **0 of 13 strategies beat buy-and-hold
with statistical significance on the one-shot holdout.** The base case for a
no-edge bot on €100–200 is **losing money to costs.**

State it plainly: **this landscape identifies the cheapest place to run a bot —
it is not evidence that a profitable bot exists.** Picking Bitvavo lowers the
cost of *finding out*; it does not raise the odds that the answer is yes. Any
go-live decision should treat expected P&L at this size as **negative until a
strategy demonstrates a real, out-of-sample, cost-beating edge**, which the
program has not found.

---

## 7. OWNER-ACTION rows (⚑)

**These are FLAG-ONLY. No agent executes any of them.** Simply opening an
account spends **no money** — funding and trading are the owner's separate,
later decisions. Conservative expectation throughout: at €100–200 with no
demonstrated edge, expect to **lose money to costs** (see §6).

⚑ **Row A — Open Bitvavo account + KYC**
- **WHAT:** owner creates a personal Bitvavo account and completes MiCA/AML KYC (ID + liveness + address).
- **WHERE:** bitvavo.com (NL-domiciled, AFM MiCA CASP).
- **HOW:** standard online signup; SEPA/iDEAL funding is free (fund later, separately — not required to open).
- **WHY:** #1 pick — lowest friction at €100–200 (pure %, no per-order floor).
- **UNBLOCKS:** everything downstream (Row B needs an account first).
- **VERIFIED-WHEN:** owner confirms the account is open and KYC-approved. *No money is spent by opening an account.*

⚑ **Row B — Generate a TRADE-only API key/secret**
- **WHAT:** owner generates a Bitvavo API key + secret scoped to **TRADE only — NOT withdraw**.
- **WHERE:** Bitvavo account → API settings.
- **HOW:** store as **ENV VAR NAMES only** — `BITVAVO_API_KEY`, `BITVAVO_API_SECRET`. **NEVER commit secret values to any repo.**
- **WHY:** least-privilege — a trade-only key cannot move funds off the exchange even if leaked.
- **UNBLOCKS:** any future bot wiring (still gated by Row C).
- **VERIFIED-WHEN:** the two env-var names exist in the owner's local/secret store with a trade-only (no-withdraw) key; no secret value in git. *Conservative expectation: a key enables testing, not profit.*

⚑ **Row C — GO-LIVE GATE (separate, FLAG-ONLY, never self-executing)**
- **WHAT:** activating **any** live bot.
- **WHERE:** this lane's standing rail.
- **HOW:** requires an **explicit owner ORDER that lifts the standing RESEARCH-ONLY rail.** **No agent activates this — ever.**
- **WHY:** RESEARCH-ONLY is the default; live trading is an owner decision, not an agent's.
- **UNBLOCKS:** live operation — **only** after the owner's explicit order.
- **VERIFIED-WHEN:** an owner order lifting the RESEARCH-ONLY rail exists. *Conservative expectation: expected P&L is negative until a real cost-beating edge is demonstrated (§6); opening/keying spends no money, going live risks real capital.*

---

## 8. Sources & uncertainties

Every UNVERIFIED flag carried forward from the source files:

- **Kraken entry fee tier** — Tier 1 now 0.80% taker per the July 2026 change;
  many reviews still quote the old 0.26%. Recorded, sourced; the *old* figure
  is UNVERIFIED/outdated. (§4 Kraken)
- **Wft article number** — the specific article for the own-account-dealing
  exemption (Art. 10a referenced) is **UNVERIFIED** against the consolidated
  legal text; the exemption principle is confirmed. (§3)
- **LYNX minimum deposit ~€3,000** — from Curvo, **UNVERIFIED** against LYNX's
  own price list. (§4 LYNX)
- **Saxo NL primary commission page** — `/nl-saxo-bank/stocks/commissions`
  returned **404** on 2026-07-12; the ~€2 EU-stock minimum rests on
  brokerchooser. (§4 Saxo)
- **Alpaca NL eligibility** — **UNVERIFIED**; no country list, only Canada
  explicitly excluded; "Alpaca Europe" is B2B infra, not retail self-serve. (§4 Alpaca)
- **CFD retail-loss exact %** — ~75–77% (Pepperstone) / ~70.6% (IC Markets EU)
  vary by reporting period; exact current figure **UNVERIFIED**. (§4 CFD)
- **Coinbase Advanced fee (~1.20% round-trip)** — secondary source,
  **UNVERIFIED** against Coinbase's own schedule. (§4 Coinbase)
- **IBKR Fixed-plan EU minimum** — IBKR pricing pages returned HTTP 403 to
  automated fetch; Tiered €1.25 is corroborated via search snippets, exact
  Fixed minimum **UNVERIFIED**. (§4 IBKR)
- **T212 NL entity (BaFin vs CySEC) + automation ToS + API rate limits** —
  **PARTIALLY VERIFIED**; confirm at signup. (§4 T212)
- **DEGIRO verbatim anti-automation clause** — **NOT FOUND** at source (helpdesk
  503s); position consistent across sources. (§4 DEGIRO)
- **Bitvavo / Kraken spot sandbox** — no confirmed public spot sandbox for
  either; paper-trade via bot dry-run or tiny live orders. (§4 Bitvavo, Kraken)
- **Paper-account provisioning at MEXEM/LYNX** (vs the underlying IBKR account)
  — **UNVERIFIED**; IBKR direct definitely offers paper trading. (§4 MEXEM, IBKR)

**Disclaimer:** all figures accessed 2026-07-12 from broker/exchange pages and
2026 secondary aggregators; schedules change without notice. General
information, **not legal or financial advice.**
