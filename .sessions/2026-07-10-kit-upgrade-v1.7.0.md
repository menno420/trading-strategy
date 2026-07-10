# 2026-07-10 — substrate-kit upgrade v1.1.0 → v1.7.0

> **Status:** `complete`

📊 Model: withheld per session policy · kit-upgrade lane · start 2026-07-10T21:00:00Z

## What was about to happen (born-red declaration)

Distribution-wave kit upgrade (kit-lab v1.7.0 wave, Q-0261.3 scope): replace the
vendored `bootstrap.py` (v1.1.0 → v1.7.0, release asset sha256-verified), run
`bootstrap.py.new upgrade` (+ `--apply-docs` for consumer-untouched planted docs),
refresh the live `.github/workflows/substrate-gate.yml` from the regenerated staged
copy, verify `check --strict` green, ship as one PR. Scope fence: kit-owned files
only — no lane-owned content (control/, claims of other lanes, existing session
cards, domain code) is touched.

## What happened (close-out)

- Vendored dist replaced v1.1.0 → **v1.7.0** — official release asset, sha256
  `00f4f4cd…5238` verified against the adjacent `release.json` before running.
- `upgrade` + post-hoc `upgrade --apply-docs`: 10 consumer-untouched planted docs
  re-rendered (CONSTITUTION, decisions, architecture, runtime_contracts,
  helper-policy, ai-project-workflow, owner-profile, question-router,
  ideas/README, .session-journal); consumer-edited/diverged docs left alone —
  exact template deltas banked in `.substrate/upgrade-report.md`.
- New plant `docs/CAPABILITIES.md`; its strict `reachable` orphan red was cleared
  by hand-applying the report's exact 2-hunk template delta to the diverged
  `docs/AGENT_ORIENTATION.md` (read-path entry + planted-doc-set line only).
- Live gate refreshed: diffed live vs staged first — byte-identical v1.1.0
  template, no host carve-outs (pytest CI already separate in `tests.yml`) —
  then copied the regenerated v1.7.0 staged gate over it.
- `python3 bootstrap.py check --strict` exit 0 on the final tree (this card
  flipped complete as the last step).
- PR #38, branch `claude/kit-upgrade-v1.7.0`. Auto-merge arm attempted once at
  creation → known "unstable status" wall (repo toggle off, standing ⚑ (c)) →
  REST squash on green per docs/collaboration-model.md.
- Not touched per Q-0261.3: `control/inbox.md`, `control/status.md` (no `kit:`
  line exists here — tree is version truth), other lanes' claims/cards, domain
  code. Open PR #37 (P5 holdout) disjoint, untouched.

## Lane-owed follow-ups (guard recipe)

- Next `control/status.md` heartbeat overwrite should add
  `kit: v1.7.0 · check: green · engaged: yes` (grammar: kit ORDER 003; file:
  `control/status.md`; the adopters-registry currency checker reads the tree
  meanwhile, so nothing is red in the interim).
- Optional hand-merge of diverged-doc deltas from `.substrate/upgrade-report.md`
  (`docs/collaboration-model.md`, `control/README.md` sections on order-claiming
  + six-field OWNER-ACTION asks).
- New conventions now live: inbox pure-append (checker exists; the v1.7.0 gate
  template does not wire `--inbox-base` yet — latent, kit-side), `claimed-by:`
  order claiming (advisory), six-field ⚑ asks (advisory), born-red ADDED-card
  advisory / MODIFIED-card locked-door gating.

💡 Session idea: the substrate gate and `tests.yml` both checkout + setup-python
on every PR; a tiny composite action (or merging tests into the gate's heavy
lane) would halve Actions cold-start time per PR — worth a look when Actions
minutes start to matter. (Kit-side idea routed via the wave log: wire
`--inbox-base` into the gate template so the 1.7.0 inbox append-only checker
actually gates CI.)

⟲ Previous-session review: the ORDER 007 close-out (#36) left an exemplary
status heartbeat — precise, claim released, next order sequenced; nothing to
fix there. One system improvement it surfaces: `check --strict` findings like
the CAPABILITIES orphan only appear *after* an upgrade plants a doc — the kit
upgrade report could pre-warn ("this plant will be unreachable given your
diverged router") so adopters fix reachability in the same pass instead of
discovering it from a red check.
