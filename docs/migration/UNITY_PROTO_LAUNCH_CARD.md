# Unity Prototype Launch Card

Branch: `codemini-isolated`

Ship one playable Unity prototype. Everything else is optional.

Success:
- runnable Unity scene or build
- web preview only if it does not slow Unity
- artifact exists before buzzer

Do not:
- turn this into orchestration work
- wait for check-ins
- expand scope before first playable result
- ask for clarification unless blocked by missing local facts

Token rules:
- mandatory
- keep prompts and status updates minimal
- use the smallest viable model for routine steps
- do one pass per step unless a hard block appears
- do not generate nonessential artifacts or commentary
- prefer fewer calls, fewer lines, fewer tokens

Hook scope:
- check `.claude/hooks` and `.claude/settings.json`
- check `.githooks`
- check any repo-local Codex/Gemini wrappers, shell scripts, Python scripts, or scheduled launch daemons if they exist

Launch:
```bash
cd /Users/jamestunick/Applications/xrA1-swarm-codemini && \
git config --local core.hooksPath .githooks && \
./.githooks/verify_branch_lock.sh && \
python3 evaluation/scripts/bootstrap_faceoff_round.py --name live-sim-faceoff && \
ROUND_DIR=$(ls -1dt evaluation/faceoff_rounds/*_live-sim-faceoff | head -n 1) && \
python3 evaluation/scripts/round_countdown.py --minutes 10 --label "ROUND" && \
python3 evaluation/scripts/run_round_gates.py --round-dir "$ROUND_DIR" --minutes 10 --start-elapsed-sec 0 --midpush-elapsed-sec 0
```

Stop when Unity is runnable. Document the delta, then quit.
