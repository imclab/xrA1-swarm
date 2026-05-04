#!/usr/bin/env python3
"""
Generate a high-visibility final report for one run directory.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate final visibility report for one run.")
    parser.add_argument("--run-dir", required=True, help="Run directory path.")
    parser.add_argument("--write-markdown", required=True, help="Output markdown file path.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if raw:
                rows.append(json.loads(raw))
    return rows


def pct(n: float, d: float) -> float:
    return (n / d * 100.0) if d else 0.0


def fmt(v: float | int | None, digits: int = 2) -> str:
    if v is None:
        return "-"
    if isinstance(v, int):
        return str(v)
    return f"{v:.{digits}f}"


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)

    manifest = read_json(run_dir / "run_manifest.json")
    results = read_jsonl(run_dir / "results.jsonl")
    events = sorted(read_jsonl(run_dir / "agent_events.jsonl"), key=lambda x: (x.get("start_ms", 0), x.get("agent_id", "")))
    tasks = read_jsonl(run_dir / "tasks.jsonl")

    task_map = {t.get("scenario_id"): t for t in tasks}

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "pass")
    hard_fail = sum(1 for r in results if r.get("status") in {"fail", "error", "blocked"})
    durations = [int(r.get("duration_ms", 0)) for r in results]
    tokens = [int(r.get("tokens_total", 0)) for r in results]
    quality = [float(r.get("quality_score")) for r in results if r.get("quality_score") is not None]

    median_ms = statistics.median(durations) if durations else 0
    avg_tokens = (sum(tokens) / len(tokens)) if tokens else 0.0
    avg_quality = (sum(quality) / len(quality)) if quality else 0.0
    speed_tasks_per_hour = (total / sum(durations) * 3600000.0) if sum(durations) else 0.0
    tokens_per_success = (sum(tokens) / passed) if passed else 0.0

    by_agent: dict[str, dict] = defaultdict(lambda: {"events": 0, "tokens": 0, "duration_ms": 0})
    for e in events:
        aid = str(e.get("agent_id", "unknown"))
        by_agent[aid]["events"] += 1
        by_agent[aid]["tokens"] += int(e.get("tokens_total", 0))
        by_agent[aid]["duration_ms"] += int(e.get("duration_ms", 0))

    max_token_row = max(results, key=lambda r: int(r.get("tokens_total", 0)), default=None)
    max_duration_row = max(results, key=lambda r: int(r.get("duration_ms", 0)), default=None)

    lines: list[str] = []
    lines.append("# Final Baseline Report")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- run_id: `{manifest.get('run_id')}`")
    lines.append(f"- provider: `{manifest.get('provider')}`")
    lines.append(f"- model: `{manifest.get('model')}`")
    lines.append(f"- sandbox: `{manifest.get('sandbox_mode')}`")
    lines.append(f"- approval: `{manifest.get('approval_policy')}`")
    lines.append(f"- dry_run: `{manifest.get('dry_run')}`")
    lines.append("")

    lines.append("## Top Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Tasks | {total} |")
    lines.append(f"| Success % | {fmt(pct(passed, total))} |")
    lines.append(f"| Hard Failure % | {fmt(pct(hard_fail, total))} |")
    lines.append(f"| Speed (tasks/hour) | {fmt(speed_tasks_per_hour)} |")
    lines.append(f"| Avg Tokens/Task | {fmt(avg_tokens, 0)} |")
    lines.append(f"| Tokens/Success | {fmt(tokens_per_success, 0)} |")
    lines.append(f"| Intelligence Score (0-5) | {fmt(avg_quality)} |")
    lines.append(f"| Median Duration (ms) | {fmt(float(median_ms), 0)} |")
    lines.append("")

    lines.append("## Scenario Outcomes")
    lines.append("")
    lines.append("| Scenario | Category | Difficulty | Status | Duration ms | Tokens | Intelligence | Why |")
    lines.append("|---|---|---|---|---:|---:|---:|---|")
    for r in sorted(results, key=lambda x: x.get("scenario_id", "")):
        sid = r.get("scenario_id")
        task = task_map.get(sid, {})
        why = "baseline comparability and visibility telemetry"
        lines.append(
            f"| {sid} | {r.get('category')} | {r.get('difficulty')} | {r.get('status')} | "
            f"{r.get('duration_ms')} | {r.get('tokens_total')} | {fmt(float(r.get('quality_score', 0.0)))} | {why} |"
        )
    lines.append("")

    lines.append("## Agent Visibility")
    lines.append("")
    lines.append("| Agent | Events | Active ms | Tokens |")
    lines.append("|---|---:|---:|---:|")
    for agent_id in sorted(by_agent.keys()):
        row = by_agent[agent_id]
        lines.append(f"| {agent_id} | {row['events']} | {row['duration_ms']} | {row['tokens']} |")
    lines.append("")

    lines.append("## Timeline (When/Where/Why)")
    lines.append("")
    lines.append("| Start ms | End ms | Scenario | Agent | What | Where | Why | Status |")
    lines.append("|---:|---:|---|---|---|---|---|---|")
    for e in events:
        start_ms = int(e.get("start_ms", 0))
        end_ms = start_ms + int(e.get("duration_ms", 0))
        lines.append(
            f"| {start_ms} | {end_ms} | {e.get('scenario_id')} | {e.get('agent_id')} | "
            f"{e.get('what')} | {e.get('where')} | {e.get('why')} | {e.get('status')} |"
        )
    lines.append("")

    lines.append("## Key Insights")
    lines.append("")
    if max_token_row:
        lines.append(
            f"- Highest token scenario: `{max_token_row.get('scenario_id')}` "
            f"with `{max_token_row.get('tokens_total')}` tokens."
        )
    if max_duration_row:
        lines.append(
            f"- Slowest scenario: `{max_duration_row.get('scenario_id')}` "
            f"at `{max_duration_row.get('duration_ms')}` ms."
        )
    lines.append(
        "- Measurement mode: hybrid. Input token count uses official endpoint when available; otherwise char/4 fallback."
    )
    lines.append("- Bird’s-eye animation: render via `evaluation/scripts/render_birdseye.py` for this run.")
    lines.append("")

    out_path = Path(args.write_markdown)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
