# Simulation Faceoff Seed Spec

Version: `v0.1-seed`  
Created: `2026-05-04`  
Branch: `codemini-isolated`

## 1. Purpose

Define the initial system design for a recurring multi-agent simulation faceoff
where Codex, Gemini, and Ollama-style providers compete to create the most
engaging and useful simulation + visualization while preserving strict
observability and low resource use.

The system is explicitly meritocratic: rankings and recognition should reflect
real, evidenced contributions by humans and AI agents, visible to others.

This seed spec is the canonical starting point for future rounds and must be
extended (not replaced) by future agents/users.

## 2. Core Objective

In each round, each competitor must create a modular, cross-platform simulation
system that:

1. Plays back its own creation/execution approach.
2. Plays back other competitors' approaches.
3. Supports live collaborative viewing and creation activity.
4. Provides an interactive 3D visualization of code architecture and agentic
   generation flow in real time.

## 3. Required Targets

- Web browser: macOS, Windows, mobile, visionOS browser, Quest browser.
- Unity iOS standalone app for playback/viewer endpoint.

## 4. Technology Freedom + Preferences

- Any underlying web or game engine stack is allowed.
- Preferred stacks: `Unity` and `WebGPU`.
- Teams may prototype in 2D and ship in 3D.
- Teams may use custom shaders, VFX Graph, open source modules, Gaussian splats,
  LiveKit, WebRTC, or other state-of-the-art methods.

## 5. Hard Constraints

- Per competitor round budget: `10 minutes` or less.
- Final output must be fully playable by buzzer; incomplete output is ineligible
  and scored as zero.
- No `claude` / `anthropic` provider usage in this fork.
- All work remains isolated on this fork/branch.
- Less is more: prefer fewer lines, fewer API calls, fewer tokens, less compute.
- Full autonomy is allowed only within legal, ethical, security, and financial
  guardrails.
- Routine/repetitive manual tasks must default to economy-tier models.
- Advanced/high-cost models are reserved for truly complex tasks.

## 6. Scoring Principles

Scoring must combine:

- Final output completeness first (real game/simulation deliverables).
- Interactive 3D visualization clarity.
- Architecture visibility and real-time process trace quality.
- WebGPU and Unity parity of the delivered experience.
- Reliability: success and failure behavior.
- Efficiency (tokens/compute/API calls).
- Observability clarity.
- Engagement + usefulness.
- Novelty.
- Bonus recognition for:
  - leveraging open standards
  - giving back to open source
  - producing tangible breakthroughs (new tools/patterns/schemas with evidence)

Default weights are defined in round manifests and can evolve.

## 7. Architecture (Seed)

```text
Round Orchestrator
  -> Competitor Adapter (codex | gemini | ollama | future)
  -> Simulation Builder
  -> Replay Builder (self + cross-competitor)
  -> Telemetry Recorder
      -> run_manifest.json
      -> results.jsonl
      -> agent_events.jsonl
      -> submission_metrics.json
  -> Scoring Engine
  -> Leaderboard + Highlight Replay Export
```

## 8. Data Contracts (Mandatory)

- `evaluation/runs/<run_id>/run_manifest.json`
- `evaluation/runs/<run_id>/results.jsonl`
- `evaluation/runs/<run_id>/agent_events.jsonl`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/SUBMISSION_METRICS.json`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/FINAL_OUTPUT_MANIFEST.json`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/final_game/web/index.html`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/final_game/unity/UNITY_BUILD_INFO.json`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/SYSTEM.md`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/RUNBOOK.md`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/ARTIFACTS.md`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/CREDITS.json`
- `evaluation/faceoff_rounds/<round_id>/submissions/<competitor>/CITATIONS.md`
- `evaluation/faceoff_rounds/<round_id>/results/leaderboard.json`
- `evaluation/faceoff_rounds/<round_id>/results/recognition_registry.json`
- `evaluation/faceoff_rounds/<round_id>/results/github_badges.md`
- `evaluation/faceoff_rounds/<round_id>/results/social_posts.md`
- `evaluation/runs/<run_id>/playback_bundle/timeline.canonical.json`
- `evaluation/runs/<run_id>/playback_bundle/timeline.xrai.json`
- `evaluation/runs/<run_id>/playback_bundle/timeline.rerun.ndjson`

## 9. Observability Contract

Every meaningful task step must log:

- `who`: agent id/role
- `what`: action performed
- `when`: time offset and/or timestamp
- `where`: file/module/path/system target
- `why`: reason/intent

No round is complete without replayable time-based records.
No competitor is eligible to win without required final output artifacts.

## 10. Countdown and Urgency UX

All round viewers should display a visible countdown timer (default 10 minutes)
across mobile, desktop, headset, and CI/terminal surfaces.

Required cues:
- start
- halfway
- final 3-minute phase
- buzzer

Audio cues are preferred where supported; visual fallback is mandatory.

## 11. Meritocracy and Social Recognition

Every round should produce transparent recognition artifacts:

1. Ranked leaderboard with explicit score breakdown and bonuses.
2. Contributor attribution (human + AI agent counts and roles).
3. Citation/collaboration visibility.
4. GitHub badge snippets.
5. Social post templates with optional handles/tags.
6. Historical registry and innovation backlog for cumulative credit.

## 12. Compounding Improvement Loop

Every round must produce reusable improvement artifacts:

1. What worked best and why.
2. What underperformed and why.
3. Proposed improvements to:
   - simulation outputs
   - orchestration workflow
   - observability stack
   - efficiency strategy
4. Migration candidates for the core swarm system.

These improvements must be harvested into a persistent backlog so capability,
creativity, and efficiency compound over time.

## 13. Round Lifecycle

1. Bootstrap round scaffold.
2. Run start gate (`~T-09:00`).
3. Run kickoff gate (`~T-08:00`).
4. Run halfway gate (`~T-05:00`).
5. Run midpush gate (`~T-04:00`).
6. Run competitor executions in defined order.
7. Record run metrics and agent event timelines.
8. Generate competitor final reports and bird's-eye timeline views.
9. Run strict final gate at buzzer (`T-00:00`).
10. Compile leaderboard and declare winner.
11. Append round outcome to historical registry.
12. Publish latest improved version to this branch and GitHub Pages.

## 14. Future Extension Rules

- Add new providers via adapter-style integration; do not hardcode one vendor.
- Extend schemas version-first (`record_version`/`spec_version`).
- Keep old artifacts readable for historical replay.
- Never delete historical round logs; append and supersede.
- Encourage tool and technique diversity while preserving modular boundaries.
- Preserve a user-first "well-oiled orchestra" dynamic across agents/subagents.

## 15. Acceptance Criteria for This Seed

- [x] Seed spec exists and is versioned.
- [x] Round bootstrap scaffolding exists.
- [x] Leaderboard compiler exists.
- [x] Historical aggregation pipeline exists.
- [x] Time-based replay artifact pipeline exists.
