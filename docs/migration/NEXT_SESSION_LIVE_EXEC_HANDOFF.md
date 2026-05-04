# Next Session Handoff: Live Simulation Faceoff

Date: `2026-05-04`  
Status: `ready for live task execution`

## Context Snapshot

- Branch lock is active on `codemini-isolated`.
- Claude provider is blocked in evaluation run tooling.
- Baseline harness + bird's-eye replay + final reporting are working.

## Immediate Mission (Next Session)

Build one fast Unity-first prototype round. The only goal is a playable Unity
result with a minimal web companion if time remains.

Execution order (default): `codex -> gemini -> ollama`.

Success definition:
- one runnable Unity prototype
- one runnable web preview if feasible
- no mid-task clarification loops
- no extra design detours
- final output usable before the buzzer

## Model Efficiency Rules (Mandatory)

- Use lower-cost models for repetitive/manual tasks by default.
- Reserve highest-capability models for complex architecture, incident, or
  high-risk tasks only.
- Log the chosen model/tier in run artifacts.

Default routing:
- `routine`: docs, formatting, simple test additions, straightforward bugfixes
  -> economy tier model.
- `complex`: architecture/security/performance/incident/multi-agent integration
  -> advanced tier model.

Provider examples:
- Codex: economy `gpt-5.4-mini`, advanced `gpt-5.5`.
- Gemini: economy flash-class local/CLI model, advanced pro-class model.
- Ollama: economy `qwen2.5:7b` / `llama3.2`, advanced `qwen2.5:14b` (if local).

## Seed Spec

Primary design source:
- [SIM_FACEOFF_SEED_SPEC.md](/Users/jamestunick/Applications/xrA1-swarm-codemini/docs/migration/SIM_FACEOFF_SEED_SPEC.md)

## Why The Last Run Failed

The confusion came from spec overload, not from needing more check-ins.

Root causes:
1. Too many simultaneous goals were in play: simulation faceoff, playback system,
   leaderboard, social assets, branch safety, metrics, and cross-platform parity.
2. The prompt treated orchestration artifacts as if they were equivalent to the
   actual deliverable, so the system spent effort organizing work instead of
   shipping a Unity prototype.
3. Success was spread across many outputs instead of one primary acceptance
   gate. That encouraged busywork and delayed concrete prototype progress.
4. The round asked for frequent visibility, which is useful for monitoring, but
   not as a substitute for a tighter objective.

What fixes it:
- one primary deliverable
- one primary acceptance gate
- one owner per task slice
- no repeated status chasing unless the build is blocked
- no scope expansion until the first playable result exists

## Required Command Sequence

```bash
cd /Users/jamestunick/Applications/xrA1-swarm-codemini

# 0) Verify branch lock guardrails are active (must pass)
git config --local core.hooksPath .githooks
./.githooks/verify_branch_lock.sh

# 1) Bootstrap round
python3 evaluation/scripts/bootstrap_faceoff_round.py --name live-sim-faceoff
ROUND_DIR=$(ls -1dt evaluation/faceoff_rounds/*_live-sim-faceoff | head -n 1)

# 2) Execute competitor runs (example run dirs captured after each run)
# CODERUN=...
# GEMRUN=...
# OLLRUN=...

# Optional CI/live urgency timer:
python3 evaluation/scripts/round_countdown.py --minutes 10 --label "ROUND"

# Optional timed milestone gate runner (start/kickoff/halfway/midpush/final)
python3 evaluation/scripts/run_round_gates.py \
  --round-dir "$ROUND_DIR" \
  --minutes 10

# Lower-noise mode (disable extra nudges):
# --start-elapsed-sec 0 --midpush-elapsed-sec 0

# 3) Compile leaderboard
python3 evaluation/scripts/compile_faceoff_leaderboard.py \
  --round-dir "$ROUND_DIR" \
  --codex-run-dir "$CODERUN" \
  --gemini-run-dir "$GEMRUN" \
  --ollama-run-dir "$OLLRUN"

# 4) Update cumulative history
python3 evaluation/scripts/update_faceoff_history.py

# 5) Generate recognition assets (badges + social + registry)
python3 evaluation/scripts/generate_recognition_assets.py --round-dir "$ROUND_DIR"

# 6) Export multi-viewer playback bundle for each run
python3 evaluation/scripts/export_timeline_interchange.py --run-dir "$CODERUN"
python3 evaluation/scripts/export_timeline_interchange.py --run-dir "$GEMRUN"
python3 evaluation/scripts/export_timeline_interchange.py --run-dir "$OLLRUN"

# 7) Build static faceoff hub used by GitHub Pages
python3 evaluation/scripts/build_faceoff_site.py \
  --rounds-root evaluation/faceoff_rounds \
  --site-root docs/faceoff

# 8) Final explicit gate validation (must pass for winner eligibility)
python3 evaluation/scripts/validate_final_outputs.py \
  --round-dir "$ROUND_DIR" \
  --checkpoint final
```

## Tighter Unity-First Launch Brief

Use this brief when the goal is rapid prototype speed, not a full faceoff:

- Build a playable Unity prototype first.
- Keep the web layer optional and minimal.
- Do not wait for check-ins to continue.
- Do not ask the user for extra detail unless the build is blocked by missing
  information that cannot be inferred locally.
- Prefer one clear scene, one interaction loop, and one visible success state.
- Stop when there is a runnable artifact, then document the delta.

## Visibility Requirements

For every competitor submission:

1. `results.jsonl` complete.
2. `agent_events.jsonl` complete (`who/what/when/where/why`).
3. `birdseye_latest.html` generated.
4. `final_report_latest.md` generated.
5. `submissions/<competitor>/SUBMISSION_METRICS.json` filled.
6. `submissions/<competitor>/INNOVATIONS.md` filled.
7. `submissions/<competitor>/SYSTEM_IMPROVEMENTS.md` filled.
8. `submissions/<competitor>/BREAKTHROUGHS.md` filled with evidence-backed discoveries.
9. `submissions/<competitor>/CREDITS.json` filled with contributor attribution.
10. `submissions/<competitor>/CITATIONS.md` filled with cross references.

## End-of-Round Publish Checklist

1. Commit updated artifacts and docs on this branch.
2. Push this branch (never `main`).
3. Publish/update GitHub Pages for this branch (workflow: `faceoff-pages`).
4. Trigger next round invitation workflow.
5. Re-run leaderboard + history update after new submissions.
