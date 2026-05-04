#!/usr/bin/env python3
"""
Summarize evaluation run artifacts into markdown tables.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


PASS_STATUS = {"pass"}
HARD_FAILURE_STATUS = {"fail", "error", "blocked"}
BLOCKED_PROVIDERS = {"claude", "anthropic"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize runs into markdown.")
    parser.add_argument("--runs-root", default="evaluation/runs", help="Root directory containing run folders.")
    parser.add_argument(
        "--write-markdown",
        default=None,
        help="Optional output markdown path. If omitted, only stdout is used.",
    )
    parser.add_argument(
        "--include-blocked-providers",
        action="store_true",
        help="Include runs whose provider is blocked by current fork policy.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            rows.append(json.loads(raw))
    return rows


def pct(n: float, d: float) -> float:
    if d <= 0:
        return 0.0
    return (n / d) * 100.0


def mean_or_none(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def median_or_none(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def fmt_float(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def summarize_records(records: list[dict]) -> dict:
    total = len(records)
    passed = sum(1 for r in records if r.get("status") in PASS_STATUS)
    hard_failures = sum(1 for r in records if r.get("status") in HARD_FAILURE_STATUS)

    durations = [float(r.get("duration_ms", 0)) for r in records]
    token_totals = [float(r.get("tokens_total", 0)) for r in records]
    quality_scores = [float(r["quality_score"]) for r in records if r.get("quality_score") is not None]

    retries = sum(int(r.get("retries", 0)) for r in records)
    interventions = sum(int(r.get("human_interventions", 0)) for r in records)
    total_duration_ms = sum(durations)
    speed_tasks_per_hour = 0.0
    if total_duration_ms > 0:
        speed_tasks_per_hour = (total / total_duration_ms) * 3600000.0

    tokens_per_success = None
    if passed > 0:
        tokens_per_success = sum(token_totals) / passed

    return {
        "total": total,
        "passed": passed,
        "success_rate_pct": pct(passed, total),
        "hard_failures": hard_failures,
        "hard_failure_rate_pct": pct(hard_failures, total),
        "median_duration_ms": median_or_none(durations),
        "avg_tokens_total": mean_or_none(token_totals),
        "tokens_per_success": tokens_per_success,
        "speed_tasks_per_hour": speed_tasks_per_hour,
        "avg_quality_score": mean_or_none(quality_scores),
        "total_retries": retries,
        "total_interventions": interventions,
        "intervention_rate_pct": pct(interventions, total),
    }


def make_markdown(run_rows: list[dict]) -> str:
    now = datetime.now(timezone.utc).isoformat()
    out: list[str] = []
    out.append("# Evaluation Summary")
    out.append("")
    out.append(f"Generated: `{now}`")
    out.append("")

    out.append("## Run-Level Summary")
    out.append("")
    out.append(
        "| Run ID | Provider | Model | Total | Success % | Hard Fail % | Speed tasks/hr | Avg Tokens | Tokens/success | Intelligence (0-5) | Intervention % |"
    )
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for run in run_rows:
        s = run["summary"]
        out.append(
            f"| {run['run_id']} | {run['provider']} | {run['model']} | "
            f"{s['total']} | {fmt_float(s['success_rate_pct'])} | {fmt_float(s['hard_failure_rate_pct'])} | "
            f"{fmt_float(s['speed_tasks_per_hour'])} | {fmt_float(s['avg_tokens_total'], 0)} | "
            f"{fmt_float(s['tokens_per_success'], 0)} | "
            f"{fmt_float(s['avg_quality_score'])} | {fmt_float(s['intervention_rate_pct'])} |"
        )

    by_model: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_category: dict[str, list[dict]] = defaultdict(list)

    for run in run_rows:
        key = (run["provider"], run["model"])
        by_model[key].extend(run["records"])
        for rec in run["records"]:
            by_category[rec.get("category", "unknown")].append(rec)

    out.append("")
    out.append("## Provider/Model Rollup")
    out.append("")
    out.append("| Provider | Model | Total | Success % | Hard Fail % | Speed tasks/hr | Avg Tokens | Tokens/success | Intelligence (0-5) |")
    out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for (provider, model), records in sorted(by_model.items()):
        s = summarize_records(records)
        out.append(
            f"| {provider} | {model} | {s['total']} | {fmt_float(s['success_rate_pct'])} | "
            f"{fmt_float(s['hard_failure_rate_pct'])} | {fmt_float(s['speed_tasks_per_hour'])} | "
            f"{fmt_float(s['avg_tokens_total'], 0)} | {fmt_float(s['tokens_per_success'], 0)} | "
            f"{fmt_float(s['avg_quality_score'])} |"
        )

    out.append("")
    out.append("## Category Rollup")
    out.append("")
    out.append("| Category | Total | Success % | Hard Fail % | Speed tasks/hr | Avg Tokens | Tokens/success | Intelligence (0-5) |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for category, records in sorted(by_category.items()):
        s = summarize_records(records)
        out.append(
            f"| {category} | {s['total']} | {fmt_float(s['success_rate_pct'])} | "
            f"{fmt_float(s['hard_failure_rate_pct'])} | {fmt_float(s['speed_tasks_per_hour'])} | "
            f"{fmt_float(s['avg_tokens_total'], 0)} | {fmt_float(s['tokens_per_success'], 0)} | "
            f"{fmt_float(s['avg_quality_score'])} |"
        )

    out.append("")
    out.append("## Gate Check Template")
    out.append("")
    out.append("- Success rate target: `>= baseline + 5%`")
    out.append("- Median duration target: `<= baseline`")
    out.append("- Token efficiency target: `<= baseline - 20%`")
    out.append("- Hard failures target: `<= baseline - 30%`")
    out.append("- Intervention rate target: `<= baseline - 25%`")
    out.append("- Quality target: `>= baseline`")
    out.append("")

    return "\n".join(out)


def main() -> int:
    args = parse_args()
    runs_root = Path(args.runs_root)
    run_rows: list[dict] = []

    if not runs_root.exists():
        raise FileNotFoundError(f"Runs root not found: {runs_root}")

    for run_dir in sorted([p for p in runs_root.iterdir() if p.is_dir()]):
        manifest_path = run_dir / "run_manifest.json"
        results_path = run_dir / "results.jsonl"

        if not manifest_path.exists():
            continue

        manifest = read_json(manifest_path)
        provider = str(manifest.get("provider", "unknown"))
        provider_norm = provider.strip().lower()
        if not args.include_blocked_providers and provider_norm in BLOCKED_PROVIDERS:
            continue
        records = read_jsonl(results_path)
        summary = summarize_records(records)

        run_rows.append(
            {
                "run_id": manifest.get("run_id", run_dir.name),
                "provider": provider,
                "model": manifest.get("model", "unknown"),
                "records": records,
                "summary": summary,
            }
        )

    markdown = make_markdown(run_rows)
    print(markdown)

    if args.write_markdown:
        out_path = Path(args.write_markdown)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
