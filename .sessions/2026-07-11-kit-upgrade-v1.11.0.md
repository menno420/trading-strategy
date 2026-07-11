# 2026-07-11 — kit upgrade: substrate-kit v1.10.1 → v1.11.0

> **Status:** `complete`

📊 Model: fable-5 · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-11

💡 **Session idea:** The carve-out scanner flagged the kit's OWN outgoing
action pins (checkout@v4 / setup-python@v5 in the old live gate) as
"host-added steps" and banked a pre-regen gate that is byte-identical to
the old staged template — a guaranteed false positive on every v1.10.1
adopter this wave (fleet-manager #72 and superbot-games #45 hit it too).
Kit idea: make the detector a THREE-WAY compare (live gate vs old staged
template vs new template) — a step present in the old staged template is
kit-owned by definition, never a host carve-out; only live-vs-old-staged
deltas are genuinely host-added.

## What happened

Vendored-kit upgrade v1.10.1 → v1.11.0 via the canonical release-asset path:
sha256-verified `bootstrap.py` asset
(`c339bd6a2eb3a139dd0106d5fd3873eb2d067f79723fccb5781d4e72a74a8d29`, tag
v1.11.0 → `640f8a1a`, release run 29152928040) + `release.json`, staged as
`bootstrap.py.new`, `python3 bootstrap.py.new upgrade` (staging inputs
self-cleaned). Payload: planted-CLAUDE.md read-first rider (HANDOFF.md at
orientation slot 2), HANDOFF.md pointer composer, gate action pins
checkout@v5 / setup-python@v6, guard-fires 10-min dedupe window, bulleted
`kit:`-line grammar leniency in currency. Kit upgrade ONLY — no domain work;
`control/inbox.md` / `control/status.md` / `tests.yml` untouched. Same-day
wave as fleet-manager #72 and superbot-games #45.

## Work log

- Pre-upgrade tree at v1.10.1 (vendored dist sha256 `fbe83ce3…`, matching the v1.10.1 release asset), synced to origin/main `ed8add3`.
- Backups: exactly ONE new bank, `.substrate/backup/bootstrap-1.10.1.py` (`fbe83ce35d1fb3b544ac58fc60ee2609eaa6c69c13d77883e9fdc5da6bbad158`, byte-equal to the pre-upgrade vendored dist). Pre-existing banks byte-untouched before/after: `bootstrap-1.1.0.py` `c12a2f55…`, `bootstrap-1.10.0.py` `ba69fc5c…`, `bootstrap-1.7.0.py` `00f4f4cd…`, `bootstrap-1.7.1.py` `2aa4fedd…`, `bootstrap-1.8.0.py` `28c5dcb6…`, `bootstrap-1.9.0.py` `55181082…`.
- KNOWN FALSE POSITIVE (wave-wide): carve-out scanner flagged `checkout@v4` + `setup-python@v5` (the kit's own outgoing pins) as host-added and banked `.substrate/backup/substrate-gate.pre-regen-4f50eb4d.yml`. Verified `git show HEAD:.substrate/ci/substrate-gate.yml | diff - <bank>` → byte-identical to the OLD staged template: nothing host-owned lost, no host-ci.yml needed; bank committed as an audit artifact. The `<sha8>` equals the pre-upgrade live-gate sha256 prefix (`4f50eb4d`).
- Regenerated gate pins `actions/checkout@v5` (line 21) + `actions/setup-python@v6` (line 80); live gate byte-identical to staged `.substrate/ci/substrate-gate.yml`. Both new pins ran GREEN on their first firing here (job 86547610391, Python 3.14.6 runner). `tests.yml` byte-untouched.
- v1.11.0 payload verified in tree: read-first rider at `.substrate/claude/CLAUDE.md:16` (HANDOFF.md orientation slot 2); `HANDOFF_POINTER_FILENAME` composer at `bootstrap.py:4885`; `GUARD_FIRES_DEDUPE_WINDOW_S = 600` at `bootstrap.py:4502`; lenient `KIT_LINE_RE` (`^(?:[-*+]\s+)?(?:\*\*[^*\n]+\*\*\s*)?kit:`) at `bootstrap.py:752`. No root HANDOFF.md planted (composer only).
- guard-fires dedupe observed live: two local `check` runs appended only ONE new `.substrate/guard-fires.jsonl` line total (v1.10.1 sessions accrued 2–3 per run); committed in this flip commit per precedent.
- `check --strict` pre-flip → exit 1, only red the designed hold: "check: HOLD (by design): session card .sessions/2026-07-11-kit-upgrade-v1.11.0.md declares an in-progress Status — the born-red session gate holds the merge red until the card flips complete. This red is the designed hold, not a defect; nothing to investigate."
- Local pytest: 223 passed in 2.49s (same suite `tests.yml` runs).
- CI live-fire on payload head `185a362`: substrate-gate run 29153839659 held RED on the locked-door lane ("card … is ADDED but this PR also touches the gate workflow itself — locked-door gate") with the in-run "would HOLD" simulation, the HOLD banner, and the `##[notice]` designed-hold annotation. Card-only first head `ced9ba8`: gate run 29153780138 also held RED (the v1.10.0 card-only hold, #40 loophole closed) — tests run 29153780132 green.
- `control/inbox.md` + `control/status.md` untouched; claim file deleted IN this flip commit (the #56 lesson).

## Previous-session review

⟲ Previous-session review: the 2026-07-11 kit-upgrade-v1.10.1 session (#57) was clean and its card is why this session was near-mechanical — the backup-hash table, verbatim HOLD lines, landing constraints (auto-merge OFF → MCP squash, branch auto-delete ON), and the claim-deleted-in-flip-commit rule all transferred directly. What it could have done better: it filed the guard-fires dedupe idea but did not record the expected checkout@v4/setup-python@v5 deprecation-warning fix's side effect — the carve-out false positive this wave — even though the pin bump was already flagged there as "owed eventually"; a one-line "when the kit bumps these pins, the carve-out scanner will likely flag the old ones" prediction would have pre-armed this wave. Workflow improvement: when a session flags a future kit-side change, also note the adopter-side symptom it will produce, so the distribution seat recognizes it as designed on first contact.

## Close-out

- Follow-ups owed to the repo's own lane (NOT done here, per distribution-seat hard scope): (1) `control/status.md` kit heartbeat line still stale — update to v1.11.0; (2) still no live root `CLAUDE.md` / `.claude/CLAUDE.md` (kit copy staged at `.substrate/claude/CLAUDE.md`) — the v1.11.0 read-first rider is invisible to workers here until the lane adopts a live CLAUDE.md; (3) `docs/CAPABILITIES.md` landing-constraints entry still owed (direct push to main BLOCKED by repository rules; auto-merge toggle OFF → MCP squash path; branch auto-delete ON — re-verified this wave).
- Merge path: repo auto-merge toggle OFF → GitHub MCP `merge_pull_request` SQUASH on green, matching #51/#54/#55/#57 precedent.
