# Final Baseline Report

- generated_utc: `2026-05-04T16:15:30.144172+00:00`
- run_id: `20260504T161517Z_codex_gpt-5.5`
- provider: `codex`
- model: `gpt-5.5`
- sandbox: `read-only`
- approval: `on-request`
- dry_run: `False`

## Top Metrics

| Metric | Value |
|---|---:|
| Tasks | 15 |
| Success % | 100.00 |
| Hard Failure % | 0.00 |
| Speed (tasks/hour) | 687.02 |
| Avg Tokens/Task | 358 |
| Tokens/Success | 358 |
| Intelligence Score (0-5) | 4.20 |
| Median Duration (ms) | 5000 |

## Scenario Outcomes

| Scenario | Category | Difficulty | Status | Duration ms | Tokens | Intelligence | Why |
|---|---|---|---|---:|---:|---:|---|
| S001 | bugfix | small | pass | 3400 | 327 | 4.40 | baseline comparability and visibility telemetry |
| S002 | bugfix | medium | pass | 5000 | 349 | 4.20 | baseline comparability and visibility telemetry |
| S003 | refactor | small | pass | 3400 | 316 | 4.40 | baseline comparability and visibility telemetry |
| S004 | refactor | medium | pass | 5000 | 363 | 4.20 | baseline comparability and visibility telemetry |
| S005 | test_generation | small | pass | 3400 | 319 | 4.40 | baseline comparability and visibility telemetry |
| S006 | test_generation | medium | pass | 5000 | 352 | 4.20 | baseline comparability and visibility telemetry |
| S007 | documentation | small | pass | 3400 | 310 | 4.40 | baseline comparability and visibility telemetry |
| S008 | documentation | medium | pass | 5000 | 343 | 4.20 | baseline comparability and visibility telemetry |
| S009 | architecture_review | medium | pass | 5000 | 352 | 4.20 | baseline comparability and visibility telemetry |
| S010 | security_review | medium | pass | 5000 | 358 | 4.20 | baseline comparability and visibility telemetry |
| S011 | performance | medium | pass | 5000 | 349 | 4.20 | baseline comparability and visibility telemetry |
| S012 | multi_agent_orchestration | large | pass | 7500 | 399 | 4.00 | baseline comparability and visibility telemetry |
| S013 | incident_response | large | pass | 7500 | 410 | 4.00 | baseline comparability and visibility telemetry |
| S014 | migration | large | pass | 7500 | 410 | 4.00 | baseline comparability and visibility telemetry |
| S015 | long_session_stability | large | pass | 7500 | 410 | 4.00 | baseline comparability and visibility telemetry |

## Agent Visibility

| Agent | Events | Active ms | Tokens |
|---|---:|---:|---:|
| planner-s001 | 1 | 900 | 26 |
| planner-s002 | 1 | 1200 | 21 |
| planner-s003 | 1 | 900 | 21 |
| planner-s004 | 1 | 1200 | 27 |
| planner-s005 | 1 | 900 | 22 |
| planner-s006 | 1 | 1200 | 22 |
| planner-s007 | 1 | 900 | 18 |
| planner-s008 | 1 | 1200 | 18 |
| planner-s009 | 1 | 1200 | 22 |
| planner-s010 | 1 | 1200 | 25 |
| planner-s011 | 1 | 1200 | 21 |
| planner-s012 | 1 | 1800 | 22 |
| planner-s013 | 1 | 1800 | 27 |
| planner-s014 | 1 | 1800 | 27 |
| planner-s015 | 1 | 1800 | 27 |
| verifier-s001 | 1 | 700 | 210 |
| verifier-s002 | 1 | 1000 | 210 |
| verifier-s003 | 1 | 700 | 210 |
| verifier-s004 | 1 | 1000 | 210 |
| verifier-s005 | 1 | 700 | 210 |
| verifier-s006 | 1 | 1000 | 210 |
| verifier-s007 | 1 | 700 | 210 |
| verifier-s008 | 1 | 1000 | 210 |
| verifier-s009 | 1 | 1000 | 210 |
| verifier-s010 | 1 | 1000 | 210 |
| verifier-s011 | 1 | 1000 | 210 |
| verifier-s012 | 1 | 1500 | 210 |
| verifier-s013 | 1 | 1500 | 210 |
| verifier-s014 | 1 | 1500 | 210 |
| verifier-s015 | 1 | 1500 | 210 |
| worker-s001 | 1 | 1800 | 91 |
| worker-s002 | 1 | 2800 | 118 |
| worker-s003 | 1 | 1800 | 85 |
| worker-s004 | 1 | 2800 | 126 |
| worker-s005 | 1 | 1800 | 87 |
| worker-s006 | 1 | 2800 | 120 |
| worker-s007 | 1 | 1800 | 82 |
| worker-s008 | 1 | 2800 | 115 |
| worker-s009 | 1 | 2800 | 120 |
| worker-s010 | 1 | 2800 | 123 |
| worker-s011 | 1 | 2800 | 118 |
| worker-s012 | 1 | 4200 | 167 |
| worker-s013 | 1 | 4200 | 173 |
| worker-s014 | 1 | 4200 | 173 |
| worker-s015 | 1 | 4200 | 173 |

## Timeline (When/Where/Why)

| Start ms | End ms | Scenario | Agent | What | Where | Why | Status |
|---:|---:|---|---|---|---|---|---|
| 0 | 900 | S001 | planner-s001 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S001.md | map prompt to measurable baseline steps | completed |
| 900 | 2700 | S001 | worker-s001 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S001.md | create reproducible evidence for benchmark pass | completed |
| 2700 | 3400 | S001 | verifier-s001 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S001.md | ensure visibility and consistency | completed |
| 3400 | 4600 | S002 | planner-s002 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S002.md | map prompt to measurable baseline steps | completed |
| 4600 | 7400 | S002 | worker-s002 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S002.md | create reproducible evidence for benchmark pass | completed |
| 7400 | 8400 | S002 | verifier-s002 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S002.md | ensure visibility and consistency | completed |
| 8400 | 9300 | S003 | planner-s003 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S003.md | map prompt to measurable baseline steps | completed |
| 9300 | 11100 | S003 | worker-s003 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S003.md | create reproducible evidence for benchmark pass | completed |
| 11100 | 11800 | S003 | verifier-s003 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S003.md | ensure visibility and consistency | completed |
| 11800 | 13000 | S004 | planner-s004 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S004.md | map prompt to measurable baseline steps | completed |
| 13000 | 15800 | S004 | worker-s004 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S004.md | create reproducible evidence for benchmark pass | completed |
| 15800 | 16800 | S004 | verifier-s004 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S004.md | ensure visibility and consistency | completed |
| 16800 | 17700 | S005 | planner-s005 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S005.md | map prompt to measurable baseline steps | completed |
| 17700 | 19500 | S005 | worker-s005 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S005.md | create reproducible evidence for benchmark pass | completed |
| 19500 | 20200 | S005 | verifier-s005 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S005.md | ensure visibility and consistency | completed |
| 20200 | 21400 | S006 | planner-s006 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S006.md | map prompt to measurable baseline steps | completed |
| 21400 | 24200 | S006 | worker-s006 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S006.md | create reproducible evidence for benchmark pass | completed |
| 24200 | 25200 | S006 | verifier-s006 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S006.md | ensure visibility and consistency | completed |
| 25200 | 26100 | S007 | planner-s007 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S007.md | map prompt to measurable baseline steps | completed |
| 26100 | 27900 | S007 | worker-s007 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S007.md | create reproducible evidence for benchmark pass | completed |
| 27900 | 28600 | S007 | verifier-s007 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S007.md | ensure visibility and consistency | completed |
| 28600 | 29800 | S008 | planner-s008 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S008.md | map prompt to measurable baseline steps | completed |
| 29800 | 32600 | S008 | worker-s008 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S008.md | create reproducible evidence for benchmark pass | completed |
| 32600 | 33600 | S008 | verifier-s008 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S008.md | ensure visibility and consistency | completed |
| 33600 | 34800 | S009 | planner-s009 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S009.md | map prompt to measurable baseline steps | completed |
| 34800 | 37600 | S009 | worker-s009 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S009.md | create reproducible evidence for benchmark pass | completed |
| 37600 | 38600 | S009 | verifier-s009 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S009.md | ensure visibility and consistency | completed |
| 38600 | 39800 | S010 | planner-s010 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S010.md | map prompt to measurable baseline steps | completed |
| 39800 | 42600 | S010 | worker-s010 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S010.md | create reproducible evidence for benchmark pass | completed |
| 42600 | 43600 | S010 | verifier-s010 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S010.md | ensure visibility and consistency | completed |
| 43600 | 44800 | S011 | planner-s011 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S011.md | map prompt to measurable baseline steps | completed |
| 44800 | 47600 | S011 | worker-s011 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S011.md | create reproducible evidence for benchmark pass | completed |
| 47600 | 48600 | S011 | verifier-s011 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S011.md | ensure visibility and consistency | completed |
| 48600 | 50400 | S012 | planner-s012 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S012.md | map prompt to measurable baseline steps | completed |
| 50400 | 54600 | S012 | worker-s012 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S012.md | create reproducible evidence for benchmark pass | completed |
| 54600 | 56100 | S012 | verifier-s012 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S012.md | ensure visibility and consistency | completed |
| 56100 | 57900 | S013 | planner-s013 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S013.md | map prompt to measurable baseline steps | completed |
| 57900 | 62100 | S013 | worker-s013 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S013.md | create reproducible evidence for benchmark pass | completed |
| 62100 | 63600 | S013 | verifier-s013 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S013.md | ensure visibility and consistency | completed |
| 63600 | 65400 | S014 | planner-s014 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S014.md | map prompt to measurable baseline steps | completed |
| 65400 | 69600 | S014 | worker-s014 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S014.md | create reproducible evidence for benchmark pass | completed |
| 69600 | 71100 | S014 | verifier-s014 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S014.md | ensure visibility and consistency | completed |
| 71100 | 72900 | S015 | planner-s015 | planned scenario execution | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S015.md | map prompt to measurable baseline steps | completed |
| 72900 | 77100 | S015 | worker-s015 | produced scenario artifact and telemetry | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S015.md | create reproducible evidence for benchmark pass | completed |
| 77100 | 78600 | S015 | verifier-s015 | validated criteria and checks | evaluation/runs/20260504T161517Z_codex_gpt-5.5/artifacts/S015.md | ensure visibility and consistency | completed |

## Key Insights

- Highest token scenario: `S013` with `410` tokens.
- Slowest scenario: `S012` at `7500` ms.
- Measurement mode: hybrid. Input token count uses official endpoint when available; otherwise char/4 fallback.
- Bird’s-eye animation: render via `evaluation/scripts/render_birdseye.py` for this run.

