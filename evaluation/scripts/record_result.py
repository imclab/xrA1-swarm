#!/usr/bin/env python3
"""
Append one scenario result row into a run's results.jsonl.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUS = {"pass", "fail", "error", "blocked", "skipped"}
BLOCKED_PROVIDERS = {"claude", "anthropic"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record one scenario result.")
    parser.add_argument("--run-dir", required=True, help="Path to one run directory.")
    parser.add_argument("--scenario-id", required=True, help="Scenario identifier, e.g. S001.")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUS), help="Result status.")
    parser.add_argument("--duration-ms", type=int, required=True, help="Wall time in milliseconds.")
    parser.add_argument("--tokens-prompt", type=int, default=0, help="Prompt/input token count.")
    parser.add_argument("--tokens-completion", type=int, default=0, help="Completion/output token count.")
    parser.add_argument("--tokens-cached", type=int, default=0, help="Cached token count.")
    parser.add_argument("--cost-usd", type=float, default=None, help="Estimated task cost in USD.")
    parser.add_argument("--retries", type=int, default=0, help="Retry count.")
    parser.add_argument("--human-interventions", type=int, default=0, help="Manual interventions.")
    parser.add_argument("--quality-score", type=float, default=None, help="0.0 - 5.0 quality score.")
    parser.add_argument("--error-type", default=None, help="Short error label for fail/error outcomes.")
    parser.add_argument("--notes", default=None, help="Optional notes.")
    parser.add_argument("--provider", default=None, help="Override provider label for this row.")
    parser.add_argument("--model", default=None, help="Override model label for this row.")
    return parser.parse_args()


def load_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_task_index(run_dir: Path) -> dict:
    tasks_path = run_dir / "tasks.jsonl"
    if not tasks_path.exists():
        raise FileNotFoundError(f"Missing tasks copy: {tasks_path}")
    index: dict[str, dict] = {}
    with tasks_path.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            row = json.loads(raw)
            sid = row.get("scenario_id")
            if sid:
                index[sid] = row
    return index


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    if args.duration_ms < 0:
        raise ValueError("--duration-ms must be >= 0")

    if args.tokens_prompt < 0 or args.tokens_completion < 0 or args.tokens_cached < 0:
        raise ValueError("token values must be >= 0")

    if args.retries < 0 or args.human_interventions < 0:
        raise ValueError("retries and interventions must be >= 0")

    if args.quality_score is not None and not (0.0 <= args.quality_score <= 5.0):
        raise ValueError("--quality-score must be between 0 and 5")

    manifest = load_manifest(run_dir)
    task_index = load_task_index(run_dir)
    task = task_index.get(args.scenario_id, {})

    provider = args.provider if args.provider is not None else manifest.get("provider")
    model = args.model if args.model is not None else manifest.get("model")
    provider_norm = str(provider).strip().lower() if provider is not None else ""
    if provider_norm in BLOCKED_PROVIDERS:
        blocked = ", ".join(sorted(BLOCKED_PROVIDERS))
        raise ValueError(
            f"Provider '{provider}' is blocked in this fork. "
            f"Blocked providers: {blocked}."
        )

    record = {
        "record_version": 1,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": manifest.get("run_id"),
        "scenario_id": args.scenario_id,
        "category": task.get("category", "unknown"),
        "difficulty": task.get("difficulty"),
        "provider": provider,
        "model": model,
        "status": args.status,
        "duration_ms": args.duration_ms,
        "tokens_prompt": args.tokens_prompt,
        "tokens_completion": args.tokens_completion,
        "tokens_cached": args.tokens_cached,
        "tokens_total": args.tokens_prompt + args.tokens_completion + args.tokens_cached,
        "cost_usd": args.cost_usd,
        "retries": args.retries,
        "human_interventions": args.human_interventions,
        "quality_score": args.quality_score,
        "error_type": args.error_type,
        "notes": args.notes,
    }

    out_path = run_dir / "results.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True))
        f.write("\n")

    print(json.dumps({"ok": True, "run_dir": str(run_dir), "scenario_id": args.scenario_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
