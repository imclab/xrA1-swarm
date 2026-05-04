# Next Session Handoff: Live Simulation Faceoff

Date: `2026-05-04`  
Status: `ready for live task execution`

## Context Snapshot

- Branch lock is active on `codemini-isolated`.
- Claude provider is blocked in evaluation run tooling.
- Baseline harness + bird's-eye replay + final reporting are working.

## Immediate Mission (Next Session)

Run a live faceoff where competitors build simulation + visualization systems in
`<= 10 minutes` each, with complete `what/when/where/why` traceability and
cross-platform design targets.

Execution order (default): `codex -> gemini -> ollama`.

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

## Required Command Sequence

```bash
cd /Users/jamestunick/Applications/xrA1-swarm-codemini

# 1) Bootstrap round
python3 evaluation/scripts/bootstrap_faceoff_round.py --name live-sim-faceoff
ROUND_DIR=$(ls -1dt evaluation/faceoff_rounds/*_live-sim-faceoff | head -n 1)

# 2) Execute competitor runs (example run dirs captured after each run)
# CODERUN=...
# GEMRUN=...
# OLLRUN=...

# Optional CI/live urgency timer:
python3 evaluation/scripts/round_countdown.py --minutes 10 --label "ROUND"

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
```

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
3. Publish/update GitHub Pages for this branch.
4. Trigger next round invitation workflow.
5. Re-run leaderboard + history update after new submissions.
