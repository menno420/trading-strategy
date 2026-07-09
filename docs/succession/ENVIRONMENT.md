# gen-2 environment spec — trading-lab lane

> **Status:** `reference` — tested setup script + env var names. NAMES ONLY; never commit values.

## Setup script
Use `environments/setup-universal.sh` (this repo) as the environment's setup script — paste its contents into the environment config. Contract: exits 0 always; assumes nothing about repo shape; installs only from each repo's own requirements.txt (or its scripts/env-setup.sh), non-fatally. Blueprint alignment: the script is synced verbatim (below the lane header) with the fleet canonical template `menno420/fleet-manager · environments/templates/setup-universal.sh` (blob 6b4459b), read at wind-down — it superseded this lane's simpler first draft because it is materially better (set +e posture, per-repo `scripts/env-setup.sh` escape hatch, `.git`-based multi/single-repo detection, unconditional exit 0 per playbook R15); this satisfies blueprint §1's "tested, shape-agnostic, defensive setup script" seed item.

**Test evidence (run at 2026-07-09T19:57:47Z, this container):**
- `bash -n environments/setup-universal.sh` → clean (output: `BASH-N: clean`, no syntax errors).
- Empty temp dir (`t1-empty`, no .git, no files): exit 0. Verbatim output:
  ```
  [env-setup] t1-empty: no scripts/env-setup.sh or requirements.txt — skipping
  [env-setup] setup complete (defensive shim: always exit 0)
  EXIT=0
  ```
- Simulated two-source checkout (`t2-multi/` containing `emptyrepo/` with only a bare `.git/` dir, and `pyrepo/` with a `.git/` dir + `requirements.txt` containing `pytest`, already installed): exit 0. Verbatim output:
  ```
  [env-setup] emptyrepo: no scripts/env-setup.sh or requirements.txt — skipping
  [env-setup] pyrepo: python3 -m pip install -r requirements.txt
  WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv
  [env-setup] setup complete (defensive shim: always exit 0)
  EXIT=0
  ```

## Environment variables required by this lane
- **None.** Market data (yfinance) is keyless; the egress proxy and its CA bundle (`REQUESTS_CA_BUNDLE`, `HTTPS_PROXY`) are platform-provided, not lane config; git/GitHub auth is platform-provided. Do not add secrets to this repo or its environment unless a future lane adds an authenticated data source — then add the NAME here first.

## Sources
Two sources: menno420/trading-strategy (primary), menno420/substrate-kit (discipline kit). Remember: with 2+ sources, session cwd is /home/user and each repo is a subdirectory — this shaped every wall in the setup-script failure class.
