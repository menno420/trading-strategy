# Paper-lane ledger — mock trades only, committed before outcomes

> **Status:** `living-ledger`
>
> The append-only paper ledger required by
> [docs/paper-lane-protocol.md](../../docs/paper-lane-protocol.md) §5.
> One record per action. **No real money, no brokerage account, no order,
> no API — ever.** Every record is committed to git BEFORE its outcome
> window opens; the git commit timestamp is the tamper evidence. Rows are
> never edited or backdated — a wrong row is corrected by a new row that
> references it. Late commit = MISS (protocol §5, §9 A3). Any ambiguity
> resolves against the strategy (protocol §9).

## Record schema

Each record carries: `id`, `committed_at_utc`, `strategy_id`, `instrument`,
`direction`, `size`, `thesis`, `entry rule`, `exit rule`,
`horizon / outcome window`, `status` — plus, for ENTRY/EXIT actions, the
protocol §5 signal-side fields: signal date, action, intended fill bar
(next trading day's open), shares at $10,000 notional, and the signal-side
numbers (close, channel values) that triggered it. WATCH rows record the
honest signal state when no action is possible or taken.

Statuses: `WATCH` (no position, no actionable signal), `ENTRY`, `EXIT`,
plus weekly-review verdicts `BEAT` / `MISS` / `FLAT` per protocol §6–§7.

---

## Records (append-only, newest last)

### paper-0001 — WATCH (lane opening; warm-up pending, zero lane bars exist)

- id: paper-0001
- committed_at_utc: 2026-07-10T21:44:51Z
- strategy_id: donchian_AAPL_daily_e15x5
- instrument: AAPL, daily bars
- direction: FLAT — no position, none possible yet
- size: $10,000 fixed notional per entry (protocol §4); $0 deployed
- thesis: forward evidence-gathering on genuinely new bars for the sole
  surviving RULE-PASS candidate, per
  [docs/paper-lane-protocol.md](../../docs/paper-lane-protocol.md)
  (pre-registered 2026-07-10; evidence-gathering only, NOT promotion).
- entry rule: long when bar *t*'s close breaks above the rolling max of
  the previous 15 bars' highs (channel shifted one bar); fill at bar
  *t+1*'s open, 5 bps slippage + 1 bps commission per side (protocol §2).
- exit rule: flat when bar *t*'s close breaks below the rolling min of
  the previous 5 bars' lows (one-bar shift); entry wins a same-bar tie;
  fill at bar *t+1*'s open, same costs (protocol §2).
- horizon / outcome window: entry fill → exit fill; no fixed calendar
  horizon; graded only after the exit fills, vs cycle-window AAPL
  buy-and-hold (protocol §6–§7).
- status: **WATCH** — strategy flat, warm-up pending.
- signal state, honest, as of 2026-07-10: PAPER_LANE_START = 2026-07-11
  is **tomorrow**. Zero paper-lane bars exist yet, so the donchian(15,5)
  channels — which per protocol §9 A1 build ONLY from bars
  ≥ 2026-07-11 — have no data: no channel value exists, no signal can be
  computed, and none was. No channel was computed from any pre-2026-07-11
  bar; no market data was read for this record. The first bar that can
  even emit an entry signal is the 16th paper-lane trading bar
  (~early August 2026); the first possible fill is the open after that
  (t+1-open on a 15-bar channel breakout, per the pre-registered rule).
  The lane starts flat and earns nothing until then (protocol §3,
  warm-up consequence — accepted, against the strategy).
