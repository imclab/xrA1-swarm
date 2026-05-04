# Unity Prototype Launch Card

Branch: `codemini-isolated`

## Goal

Ship one playable Unity prototype as fast as possible.

## Success

- One runnable Unity scene or build.
- One minimal web preview only if it does not slow Unity delivery.
- Final artifact exists before the buzzer.

## Do Not Do

- Do not turn this into a faceoff orchestration exercise.
- Do not wait for frequent status check-ins.
- Do not expand scope until the first playable result exists.
- Do not ask for clarification unless the build is blocked by missing local facts.

## Root Cause To Avoid

The last run drifted because the spec contained too many parallel goals:
faceoff scoring, playback, branch safety, observability, social assets, and
cross-platform parity. That is useful for the full system, but it is too much
for a fast prototype round. The next run must optimize for shipping one Unity
prototype first.

## Launch Sequence

```bash
cd /Users/jamestunick/Applications/xrA1-swarm-codemini
git config --local core.hooksPath .githooks
./.githooks/verify_branch_lock.sh

python3 evaluation/scripts/bootstrap_faceoff_round.py --name live-sim-faceoff
ROUND_DIR=$(ls -1dt evaluation/faceoff_rounds/*_live-sim-faceoff | head -n 1)

python3 evaluation/scripts/round_countdown.py --minutes 10 --label "ROUND"
python3 evaluation/scripts/run_round_gates.py --round-dir "$ROUND_DIR" --minutes 10 --start-elapsed-sec 0 --midpush-elapsed-sec 0
```

## Acceptance

- The first deliverable should be playable, not polished.
- The prototype should prove the Unity path works.
- If the web companion is easy, add it after Unity is working.

## Stop Condition

Stop once there is a runnable Unity result and write the delta. Do not keep
reworking the brief.
