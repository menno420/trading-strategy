# 2026-07-16 — Main CI triggers: schedule + workflow_dispatch on both workflows

> **Status:** `complete`

- **📊 Model:** Fable · medium effort · CI-plumbing task-class

⚑ Scope (claimed, `control/claims/2026-07-16-main-ci-triggers.md`, branch
`claude/main-ci-triggers`): close the GITHUB_TOKEN-merge → no-push-CI gap.
Main has had NO push-triggered CI run since `7d6aa67` (2026-07-14) because
the auto-merge enabler merges with `GITHUB_TOKEN`, whose pushes never fire
`on: push` workflows — every later main SHA is only green-by-proxy via its
PR-head checks. Fix: add `schedule:` (cron `23 */6 * * *`, every 6h at an
off-minute) AND `workflow_dispatch:` to the `on:` blocks of BOTH
`.github/workflows/tests.yml` and `.github/workflows/substrate-gate.yml`.
Minimal diff — only the `on:` blocks change; existing triggers preserved
byte-identical. Provenance: coordinator dispatch per the 2026-07-16
post-reboot-restamp session card's 💡 fix proposal. Rails: pure CI
plumbing — no strategy/executor/broker code, no secrets/PATs, no trigger
create/delete/fire, `control/inbox.md` byte-untouched.

## Plan

1. Claim + this born-red card as first commit; push; open READY PR. ✅
2. Read both workflow files fully; add the two triggers to each `on:`
   block; check event-context assumptions and the born-red HOLD behavior
   on schedule runs against main. ✅
3. Validate YAML; actionlint if available (not installed — skipped). ✅
4. Carve-out check on the auto-merge enabler at main HEAD. ✅
5. Flip this card `complete` with evidence; drive PR to terminal state. ✅

## Close-out

**What shipped:** PR #133 (`claude/main-ci-triggers` from main `9fc7ad5`).
Commit `a4fe65f` — born-red card + claim. Commit `9eb6489` — the fix: +3
lines each to `.github/workflows/tests.yml` and
`.github/workflows/substrate-gate.yml` (`schedule: - cron: '23 */6 * * *'`
+ `workflow_dispatch:` appended to each `on:` block; everything else
byte-identical, 6 insertions / 0 deletions total).

**Event-context analysis (why no extra guards were needed):** tests.yml is
event-agnostic (checkout + pytest). substrate-gate on `schedule`/
`workflow_dispatch` has empty `github.base_ref` and `github.event.before`,
so its diff range degenerates to `..<sha>` — an empty diff — which fails
safe onto the full-suite lane (`control_only=false`) and then the
no-card-in-diff advisory-sentinel branch (`--session-log
.sessions/__no-card-in-diff__.md`). On main every card is `complete`, so a
scheduled run passes; the born-red HOLD only bites on PR diffs that touch
cards. No `github.event.pull_request` references exist in either workflow.

**Verification:** `python3 -c "import yaml; yaml.safe_load(open('.github/
workflows/tests.yml')); yaml.safe_load(open('.github/workflows/
substrate-gate.yml'))"` → exit 0 (`YAML-OK`). actionlint not installed —
skipped, not attempted-installed. This PR itself exercises the edited
substrate-gate (a PR touching the gate file runs the NEW gate from the PR
head, and the gate-regen branch applies the locked-door +
`--simulate-added-card` lane to this very card — red until this flip, by
design). First scheduled fire expected at the next `23 */6` boundary after
merge.

**Carve-out verdict:** `.github/workflows/auto-merge-enabler.yml` @ main
`9fc7ad5` has NO path-based carve-out — the only arming conditions are the
job-level `if` (lines 40–44: same-repo head, non-draft, `claude/*` branch,
no `do-not-automerge` label), the zero-required-contexts refusal (lines
47–63), and the fresh label re-read (lines 64–85). Nothing inspects the
PR's changed files, so a workflows-touching PR arms and lands like any
other.

**Previous-session review:** the 2026-07-16 post-reboot-restamp card is a
model of the form — its 💡 idea line (this exact fix, with anchors and a
verify target) made this session dispatchable with near-zero re-derivation;
its one miss is that it proposed "daily" where 6-hourly was the better
staleness bound, a judgment call the dispatch corrected.

💡 **Session idea (deduped against prior cards):** both edited files are
KIT-OWNED — `substrate-gate.yml`'s own header says adopt/upgrade
REGENERATES it in place and hand edits are OVERWRITTEN — so the next
`bootstrap.py upgrade` will silently strip these schedule/dispatch
triggers. Durable fix per the header's own guidance: move the periodic
main verification into a SEPARATE host-owned workflow file (e.g.
`.github/workflows/main-cron-verify.yml`, `schedule` + `workflow_dispatch`
only, jobs that just invoke the same pytest + `bootstrap.py check
--strict` commands), or upstream the trigger addition into the kit
template. Anchors: `.github/workflows/substrate-gate.yml` header lines
1–6, `bootstrap.py upgrade` path; verify target: post-upgrade `git diff`
on the two workflow `on:` blocks.

Integrity at close: diff vs main touches only the two workflow `on:`
blocks, this card, and the claim lifecycle (created first commit, deleted
this commit). `control/inbox.md` byte-untouched; no strategy/executor/
broker code; no secrets/PATs; no trigger created/modified/fired;
family-level model attribution only; landing path is the auto-merge
enabler, not a merge action by this session.

Session end: badge flipped `complete` in this final content commit before
push.
