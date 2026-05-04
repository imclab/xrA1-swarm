# Phase 0 Evaluation Harness

This folder is the Phase 0 baseline harness for `xrA1-swarm-codemini`.

Scope of Phase 0:
- Build measurement scaffolding only.
- Do not swap runtimes yet.
- Do not modify `.claude` behavior yet.
- Keep all work isolated to this fork/branch.
- Enforce provider policy: `claude`/`anthropic` are blocked in this fork.

## Folder Layout

- `tasks/baseline_tasks.jsonl`: canonical scenario set for A/B runs.
- `schemas/run_result.schema.json`: JSON schema for per-scenario results.
- `scripts/init_run.py`: creates a timestamped run directory and manifest.
- `scripts/record_result.py`: appends a structured result row to `results.jsonl`.
- `scripts/summarize.py`: generates markdown summaries and rollups.
- `scripts/log_agent_event.py`: logs agent-level activity events (`what/where/why`).
- `scripts/render_birdseye.py`: renders animated bird's-eye HTML timeline from events.
- `scripts/run_full_pass.py`: executes all baseline scenarios with consistent telemetry.
- `scripts/generate_final_report.py`: creates one high-visibility report for a run.
- `scripts/bootstrap_faceoff_round.py`: creates a new competitor round scaffold.
- `scripts/compile_faceoff_leaderboard.py`: scores competitor runs for a round (final output gate: web + Unity + docs).
- `scripts/update_faceoff_history.py`: aggregates completed rounds into history logs.
- `scripts/generate_recognition_assets.py`: emits badges/social/recognition registry.
- `scripts/export_timeline_interchange.py`: emits canonical/XRAI/Rerun-compatible timeline bundle.
- `scripts/round_countdown.py`: countdown cues for CI/terminal urgency tracking.
- `scripts/build_faceoff_site.py`: builds static faceoff hub (`docs/faceoff`) for GitHub Pages.
- `scripts/validate_final_outputs.py`: checkpoint/final gate validation for shipped deliverables.
- `scripts/run_round_gates.py`: timed kickoff/halfway/final gate runner over the round window.
- `runs/`: local run artifacts (ignored except `.gitkeep`).
- `reports/`: generated summary reports (ignored except `.gitkeep`).

## Quick Start

1. Initialize a run:

```bash
python3 evaluation/scripts/init_run.py \
  --provider codex \
  --model gpt-5.5 \
  --sandbox read-only \
  --approval on-request \
  --dry-run
```

2. Record one scenario result:

```bash
python3 evaluation/scripts/record_result.py \
  --run-dir evaluation/runs/<run_id> \
  --scenario-id S001 \
  --status pass \
  --duration-ms 41000 \
  --tokens-prompt 1200 \
  --tokens-completion 250 \
  --quality-score 4.2
```

3. Build summary:

```bash
python3 evaluation/scripts/summarize.py \
  --runs-root evaluation/runs \
  --write-markdown evaluation/reports/latest_summary.md
```

By default, summaries exclude blocked providers (`claude`, `anthropic`).

4. Log agent events (`who/what/when/where/why`):

```bash
python3 evaluation/scripts/log_agent_event.py \
  --run-dir evaluation/runs/<run_id> \
  --scenario-id S001 \
  --agent-id planner-1 \
  --agent-role orchestrator \
  --what "decomposed task" \
  --where "evaluation/tasks/baseline_tasks.jsonl" \
  --why "prepare bounded execution plan" \
  --status completed \
  --start-ms 0 \
  --duration-ms 1200 \
  --tokens-prompt 80 \
  --tokens-completion 20
```

5. Render bird's-eye animation:

```bash
python3 evaluation/scripts/render_birdseye.py \
  --run-dir evaluation/runs/<run_id> \
  --round-minutes 10 \
  --write-html evaluation/reports/birdseye_latest.html
```

6. Full 15-scenario pass + final report:

```bash
python3 evaluation/scripts/run_full_pass.py \
  --provider codex \
  --model gpt-5.5 \
  --sandbox read-only \
  --approval on-request

RUN_DIR=$(ls -1dt evaluation/runs/*_codex_* | head -n 1)
python3 evaluation/scripts/render_birdseye.py \
  --run-dir "$RUN_DIR" \
  --write-html evaluation/reports/birdseye_latest.html
python3 evaluation/scripts/generate_final_report.py \
  --run-dir "$RUN_DIR" \
  --write-markdown evaluation/reports/final_report_latest.md
```

7. Faceoff round bootstrap + leaderboard + history:

```bash
python3 evaluation/scripts/bootstrap_faceoff_round.py --name live-sim-faceoff
ROUND_DIR=$(ls -1dt evaluation/faceoff_rounds/*_live-sim-faceoff | head -n 1)

# Fill competitor run dirs after each live execution:
# CODERUN=...
# GEMRUN=...
# OLLRUN=...

python3 evaluation/scripts/compile_faceoff_leaderboard.py \
  --round-dir "$ROUND_DIR" \
  --codex-run-dir "$CODERUN" \
  --gemini-run-dir "$GEMRUN" \
  --ollama-run-dir "$OLLRUN"

python3 evaluation/scripts/update_faceoff_history.py
python3 evaluation/scripts/generate_recognition_assets.py --round-dir "$ROUND_DIR"
python3 evaluation/scripts/export_timeline_interchange.py --run-dir "$CODERUN"
python3 evaluation/scripts/round_countdown.py --minutes 10 --label "ROUND"

# Build static faceoff hub for branch-scoped GitHub Pages deployment
python3 evaluation/scripts/build_faceoff_site.py \
  --rounds-root evaluation/faceoff_rounds \
  --site-root docs/faceoff

# Optional timed gate monitor for kickoff/halfway/final checks
python3 evaluation/scripts/run_round_gates.py \
  --round-dir "$ROUND_DIR" \
  --minutes 10
```

Final output gate requirements (per competitor):
- `submissions/<competitor>/final_game/web/index.html`
- `submissions/<competitor>/final_game/unity/UNITY_BUILD_INFO.json`
- `submissions/<competitor>/SYSTEM.md`
- `submissions/<competitor>/RUNBOOK.md`
- `submissions/<competitor>/ARTIFACTS.md`

Primary judged dimensions for finals:
- interactive 3D visualization clarity
- real-time architecture/process visibility
- WebGPU/Unity parity
- efficiency and reliability support metrics

`compile_faceoff_leaderboard.py` sets `final_score=0` when required final outputs
are missing (unless explicitly overridden with `--no-output-gate`).

Checkpoint recommendations:
- kickoff gate around `T-08:00`
- halfway gate around `T-05:00`
- strict final gate at `T-00:00`

Open standards/open source and breakthrough discovery are bonus-scored in the
leaderboard when `SUBMISSION_METRICS.json` includes:
- `open_standards_score_0_to_5`
- `open_source_contribution_score_0_to_5`
- `breakthrough_score_0_to_5`

## Status Values

Allowed `status` values:
- `pass`
- `fail`
- `error`
- `blocked`
- `skipped`

## Gate Targets (Phase 0 Baseline Tracking)

These are stored for comparison and not enforced by script:
- success rate >= baseline + 5%
- median duration <= baseline
- tokens per task <= baseline - 20%
- hard failures <= baseline - 30%
- manual interventions <= baseline - 25%
- quality score >= baseline
