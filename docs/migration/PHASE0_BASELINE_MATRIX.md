# Phase 0 Baseline Matrix

This document is the at-a-glance map for current state, target state, and
controlled rollout flow.

## System Matrix

| Layer | Original Claude-Coupled State | Phase 0 Output (Now) | Target Multi-Provider State |
|---|---|---|---|
| Branch safety | Manual habits + mixed workflows | Local branch lock + push guard active | Hard-guarded isolated release workflow |
| Agent instructions | `CLAUDE.md` + `.claude/*` | Baseline measured without migration | `AGENTS.md` + provider-neutral instruction chain |
| Hooks and policy | Claude hook schema in `.claude/settings.json` | No runtime edits yet | Neutral policy layer + Codex rules/hooks + adapters |
| Agent definitions | `.claude/agents/*.md` with `haiku/sonnet/opus` | Inventory complete | Alias-based provider routing (`fast`,`balanced`,`deep`) |
| Skills | `.claude/skills/*` with Claude tool semantics | Bench scenarios defined | Provider-neutral orchestration + compatibility shims |
| Telemetry | Partial logging, inconsistent metrics | Standardized `results.jsonl` + `agent_events.jsonl` + bird's-eye HTML timeline | Continuous eval with regression gates |
| Sandbox discipline | Session-specific | Explicit run manifest fields (`sandbox`,`approval`,`dry_run`) | Per-provider profiles with reproducible sandbox policy |
| Provider policy | Claude-first assumptions | `claude`/`anthropic` blocked for runs in this fork | Multi-provider router without single-vendor lock |

## Architecture Flow

```text
Task Intake
  -> Policy Gate (branch lock, sandbox policy, approval policy)
  -> Orchestrator
    -> Adapter Router
      -> Claude Adapter (baseline only in Phase 0)
      -> Codex Adapter (Phase 1+)
      -> Gemini/Ollama/LM Studio adapters (Phase 2+)
    -> Result Normalizer
  -> Metrics Recorder (JSONL)
  -> Summary + Gate Decision
```

## Incremental Dry-Run Ladder

| Stage | Sandbox | Writes | Network | Goal |
|---|---|---|---|---|
| 0A | read-only | none | allowed only for docs/research | Establish baseline behavior |
| 0B | workspace-write | isolated run artifacts only | restricted | Validate harness correctness |
| 1A | workspace-write | controlled code edits | restricted | Codex parity tests |
| 1B | workspace-write | broader edits | restricted | Codex quality/speed validation |
| 2A | workspace-write | adapter expansion | restricted | Gemini/Ollama/LM Studio parity |
| 2B | workspace-write | multi-provider orchestration | restricted | Best-provider selection per task |

## Gate Metrics

| Metric | Pass Condition |
|---|---|
| Success rate | `>= baseline + 5%` |
| Median duration | `<= baseline` |
| Tokens per task | `<= baseline - 20%` |
| Hard failures (`fail/error/blocked`) | `<= baseline - 30%` |
| Human interventions | `<= baseline - 25%` |
| Quality score (0-5) | `>= baseline` |

## Phase 0 Deliverables Checklist

- [x] Task baseline dataset (`evaluation/tasks/baseline_tasks.jsonl`)
- [x] Result schema (`evaluation/schemas/run_result.schema.json`)
- [x] Run initialization script (`evaluation/scripts/init_run.py`)
- [x] Result recording script (`evaluation/scripts/record_result.py`)
- [x] Summary generator (`evaluation/scripts/summarize.py`)
- [x] Artifact ignore rules for run data and reports
