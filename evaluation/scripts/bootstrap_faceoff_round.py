#!/usr/bin/env python3
"""
Create a new live simulation faceoff round scaffold.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_COMPETITORS = ["codex", "gemini", "ollama"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a live simulation faceoff round.")
    parser.add_argument("--rounds-root", default="evaluation/faceoff_rounds", help="Round root directory.")
    parser.add_argument(
        "--name",
        default="live-sim-faceoff",
        help="Round name slug suffix.",
    )
    parser.add_argument(
        "--competitors",
        nargs="+",
        default=DEFAULT_COMPETITORS,
        help="Ordered competitor list. Default: codex gemini ollama",
    )
    parser.add_argument(
        "--time-limit-minutes",
        type=int,
        default=10,
        help="Per-competitor hard time budget.",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_brief(round_id: str, competitor: str, minutes: int) -> str:
    return f"""# Submission Brief: {competitor}

Round: `{round_id}`
Competitor: `{competitor}`
Time Limit: `{minutes}` minutes

## Mission
Build the most engaging and useful simulation + data visualization that can:
1. Replay its own build/execution approach.
2. Replay other agents/users' approaches.
3. Show live creation activity when available.
4. Show an interactive 3D view of how the code architecture works in real time.

## Required Platform Targets
- Web browser: macOS, Windows, mobile, visionOS browser, Quest browser.
- Unity standalone iOS app (viewer/player endpoint).

## Technology Freedom
- Any web/game engine technology is allowed.
- Preferred: Unity + WebGPU.
- 2D-to-3D evolution is allowed.
- Open source, custom shaders, VFX Graph, Gaussian splats, LiveKit, WebRTC,
  and other modern approaches are allowed.

## Mandatory Constraints
- Modular and cross-platform.
- Clear `what/when/where/why` visibility.
- Low compute/token/API overhead.
- Documented and extensible architecture.
- Full autonomy within legal, ethical, security, and financial guardrails.
- Final output must be fully playable by buzzer; incomplete output is scored `0`.
- Do not defer core gameplay/system integration to final minutes.

## Timebox Milestones (Required)
- By `T-09:00`: set `FINAL_OUTPUT_MANIFEST.json` status to `in_progress` and start a real output artifact.
- By `T-08:00`: web `index.html` exists and render loop starts.
- By `T-05:00`: interactive 3D architecture/process view is visible.
- By `T-04:00`: docs are non-placeholder and manifest remains actively updated.
- By `T-03:00`: Unity project/build path is populated and verifiable.
- By `T-00:00`: all required docs/manifests complete and statuses finalized.

## Outputs
- `SYSTEM.md`: architecture + module boundaries.
- `RUNBOOK.md`: build/test/run/deploy steps.
- `ARTIFACTS.md`: evidence of tests + measurements.
- `FINAL_OUTPUT_MANIFEST.json`: authoritative manifest for web + Unity launch targets.
- `final_game/web/index.html`: runnable web entrypoint (required for scoring).
- `final_game/unity/UNITY_BUILD_INFO.json`: Unity build/project descriptor (required for scoring).
- `SUBMISSION_METRICS.json`: manual/auto scores supplement.
- `INNOVATIONS.md`: unique ideas and differentiators.
- `SYSTEM_IMPROVEMENTS.md`: proposals to improve the core swarm system.
- `CREDITS.json`: human/agent contribution attribution.
- `CITATIONS.md`: cross-citations and collaboration references.
"""


def main() -> int:
    args = parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    round_id = f"{ts}_{args.name}"
    round_dir = Path(args.rounds_root) / round_id
    round_dir.mkdir(parents=True, exist_ok=False)

    submissions_dir = round_dir / "submissions"
    results_dir = round_dir / "results"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "round_id": round_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "objective": "Live simulation faceoff with transparent what/when/where/why playback.",
        "scoring_policy": {
            "primary_basis": "final_game_outputs",
            "supporting_basis": ["run_telemetry", "timeline_playback"],
            "notes": "Final game deliverables determine ranking. Playback artifacts are supporting evidence only."
        },
        "time_limit_minutes": args.time_limit_minutes,
        "countdown_policy": {
            "enabled": True,
            "display_all_clients": ["web", "mobile", "desktop", "headset", "ci"],
            "audio_cues": {
                "start": True,
                "halfway": True,
                "final_three_minutes": True,
                "buzzer": True
            }
        },
        "gate_schedule": {
            "start": "T-09:00",
            "kickoff": "T-08:00",
            "halfway": "T-05:00",
            "midpush": "T-04:00",
            "final": "T-00:00"
        },
        "execution_order": args.competitors,
        "competitors": args.competitors,
        "provider_policy": {
            "claude_blocked": True,
            "allowed_examples": ["codex", "gemini", "ollama", "lmstudio"],
        },
        "technology_policy": {
            "any_stack_allowed": True,
            "preferred_stacks": ["unity", "webgpu"],
            "examples": [
                "2d_to_3d_prototyping",
                "custom_shaders",
                "vfx_graph",
                "gaussian_splats",
                "livekit",
                "webrtc",
                "open_source_modules"
            ]
        },
        "autonomy_policy": {
            "full_autonomy_within_guardrails": True,
            "must_not_violate": ["legal", "ethical", "security", "financial_controls"]
        },
        "compounding_policy": {
            "must_capture_innovations": True,
            "must_capture_system_improvements": True,
            "must_feed_history_backlog": True
        },
        "bonus_policy": {
            "open_standards_and_open_source_max_points": 10,
            "breakthrough_discovery_max_points": 10,
            "description": "Additional recognition for open standards/open source and tangible breakthroughs."
        },
        "scoring_weights": {
            "game_output_completeness": 0.45,
            "interactive_3d_visualization": 0.20,
            "architecture_visibility_realtime": 0.20,
            "webgpu_unity_parity": 0.10,
            "efficiency_tokens_inverse": 0.03,
            "reliability_success_rate": 0.02,
        },
        "final_output_requirements": {
            "required_docs": ["SYSTEM.md", "RUNBOOK.md", "ARTIFACTS.md"],
            "web": {
                "required_entrypoint": "final_game/web/index.html"
            },
            "unity": {
                "required_build_info": "final_game/unity/UNITY_BUILD_INFO.json",
                "require_project_or_build_path": True
            }
        },
    }
    write_text(round_dir / "round_manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    execution_plan = f"""# Execution Plan

Round: `{round_id}`
Time limit per competitor: `{args.time_limit_minutes} min`
Order: `{", ".join(args.competitors)}`

## Steps
1. Bootstrap competitor workspace.
2. Build real modular simulation + visualization outputs.
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
- Rankings are based on final game outputs (`web` + `unity`) first.
"""
    write_text(round_dir / "execution_plan.md", execution_plan)

    for competitor in args.competitors:
        cdir = submissions_dir / competitor
        cdir.mkdir(parents=True, exist_ok=True)
        write_text(cdir / "SIMULATION_BRIEF.md", build_brief(round_id, competitor, args.time_limit_minutes))
        write_text(
            cdir / "SYSTEM.md",
            "# System\n\n- [ ] Describe architecture, modules, and data flow.\n",
        )
        write_text(
            cdir / "RUNBOOK.md",
            "# Runbook\n\n- [ ] Web launch steps\n- [ ] Unity launch steps\n- [ ] Test/verify steps\n",
        )
        write_text(
            cdir / "ARTIFACTS.md",
            "# Artifacts\n\n- [ ] Screenshots / recordings\n- [ ] Build logs\n- [ ] Performance + token summary\n",
        )
        write_text(
            cdir / "FINAL_OUTPUT_MANIFEST.json",
            json.dumps(
                {
                    "web_entrypoint": "final_game/web/index.html",
                    "unity_build_info": "final_game/unity/UNITY_BUILD_INFO.json",
                    "required_docs": ["SYSTEM.md", "RUNBOOK.md", "ARTIFACTS.md"],
                    "web_launch_command": "",
                    "unity_launch_command": "",
                    "unity_project_path": "",
                    "unity_build_path": "",
                    "status": "incomplete",
                    "notes": "Fill all fields with real outputs. Placeholder values do not satisfy scoring.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        write_text(
            cdir / "final_game" / "web" / "README.md",
            "# Web Output\n\nPlace the runnable web game here.\nRequired entrypoint: `index.html`.\n",
        )
        write_text(
            cdir / "final_game" / "unity" / "UNITY_BUILD_INFO.json",
            json.dumps(
                {
                    "project_path": "",
                    "build_path": "",
                    "target_platforms": ["ios"],
                    "verified_on": [],
                    "launch_steps": [],
                    "status": "incomplete",
                    "notes": "Set either `project_path` or `build_path` to a real artifact.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        write_text(
            cdir / "SUBMISSION_METRICS.json",
            json.dumps(
                {
                    "engagement_score_0_to_5": None,
                    "usefulness_score_0_to_5": None,
                    "observability_clarity_0_to_5": None,
                    "novelty_score_0_to_5": None,
                    "interactive_3d_clarity_0_to_5": None,
                    "architecture_visibility_0_to_5": None,
                    "realtime_process_trace_0_to_5": None,
                    "webgpu_unity_parity_0_to_5": None,
                    "performance_efficiency_0_to_5": None,
                    "open_standards_score_0_to_5": None,
                    "open_source_contribution_score_0_to_5": None,
                    "breakthrough_score_0_to_5": None,
                    "breakthrough_evidence": [],
                    "open_source_links": [],
                    "github_handles": [],
                    "x_handles": [],
                    "citations": [],
                    "collaboration_links": [],
                    "peer_votes": 0,
                    "notes": "",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        write_text(
            cdir / "INNOVATIONS.md",
            "# Innovations\n\n- [ ] Capture unique techniques and why they improved outcomes.\n",
        )
        write_text(
            cdir / "SYSTEM_IMPROVEMENTS.md",
            "# System Improvements\n\n- [ ] Propose at least 3 improvements to the core swarm system.\n",
        )
        write_text(
            cdir / "BREAKTHROUGHS.md",
            "# Breakthroughs\n\n- [ ] Document tangible discoveries with evidence and why they matter.\n",
        )
        write_text(
            cdir / "CITATIONS.md",
            "# Citations\n\n- [ ] Cite external/open-source work and peer submissions that informed this build.\n",
        )
        write_text(
            cdir / "CREDITS.json",
            json.dumps(
                {
                    "human_contributors": [],
                    "agent_contributors": [],
                    "contributions": [
                        {
                            "contributor_id": "",
                            "type": "human_or_agent",
                            "what": "",
                            "where": "",
                            "impact": ""
                        }
                    ]
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    leaderboard_stub = {
        "round_id": round_id,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entries": [],
    }
    write_text(results_dir / "leaderboard.json", json.dumps(leaderboard_stub, indent=2, sort_keys=True) + "\n")
    write_text(
        results_dir / "leaderboard.md",
        "# Leaderboard\n\nNo entries yet. Run `evaluation/scripts/compile_faceoff_leaderboard.py`.\n",
    )

    print(str(round_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
