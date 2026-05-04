# Execution Plan

Round: `20260504T093652Z_live-sim-faceoff-r2`
Time limit per competitor: `10 min`
Order: `codex, gemini, ollama`

## Steps
1. Bootstrap competitor workspace.
2. Build minimal modular simulation + visualization.
3. Capture telemetry in `evaluation/runs/*`.
4. Render bird's-eye timeline.
5. Run countdown utility (`round_countdown.py`) in CI/terminal.
6. Generate competitor final report.
7. Compile round leaderboard.

## Hard Rules
- No `claude`/`anthropic` providers in this fork.
- Keep all writes on this branch/fork only.
- Record `what/when/where/why` for each task step.
- Prefer less code and fewer API calls when outcomes are equivalent.
