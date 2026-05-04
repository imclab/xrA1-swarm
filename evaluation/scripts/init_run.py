#!/usr/bin/env python3
"""
Initialize a new evaluation run directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BLOCKED_PROVIDERS = {"claude", "anthropic"}


def git_value(args: list[str], fallback: str) -> str:
    try:
        output = subprocess.check_output(args, stderr=subprocess.DEVNULL, text=True).strip()
        return output if output else fallback
    except Exception:
        return fallback


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-").lower()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new evaluation run scaffold.")
    parser.add_argument("--provider", required=True, help="Provider label: claude/codex/gemini/ollama/lmstudio/etc.")
    parser.add_argument("--model", required=True, help="Model label used for this run.")
    parser.add_argument("--sandbox", default="read-only", help="Sandbox mode label.")
    parser.add_argument("--approval", default="on-request", help="Approval policy label.")
    parser.add_argument("--dry-run", action="store_true", help="Mark run as dry-run.")
    parser.add_argument("--operator", default=None, help="Optional operator identifier.")
    parser.add_argument("--tasks", default="evaluation/tasks/baseline_tasks.jsonl", help="Task set path.")
    parser.add_argument("--runs-root", default="evaluation/runs", help="Run artifact root path.")
    parser.add_argument("--phase", default="phase0-baseline", help="Evaluation phase label.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    provider_normalized = args.provider.strip().lower()
    if provider_normalized in BLOCKED_PROVIDERS:
        blocked = ", ".join(sorted(BLOCKED_PROVIDERS))
        raise ValueError(
            f"Provider '{args.provider}' is blocked in this fork. "
            f"Blocked providers: {blocked}."
        )

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%SZ")

    provider_slug = slug(args.provider)
    model_slug = slug(args.model)
    run_id = f"{ts}_{provider_slug}_{model_slug}"

    runs_root = Path(args.runs_root)
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    tasks_path = Path(args.tasks)
    if not tasks_path.exists():
        raise FileNotFoundError(f"Task file not found: {tasks_path}")

    shutil.copy2(tasks_path, run_dir / "tasks.jsonl")
    (run_dir / "results.jsonl").write_text("", encoding="utf-8")
    (run_dir / "agent_events.jsonl").write_text("", encoding="utf-8")

    branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], "unknown")
    commit = git_value(["git", "rev-parse", "--short", "HEAD"], "unknown")
    top = git_value(["git", "rev-parse", "--show-toplevel"], str(Path.cwd()))

    manifest = {
        "run_id": run_id,
        "created_at_utc": now.isoformat(),
        "phase": args.phase,
        "repo_root": top,
        "branch": branch,
        "commit": commit,
        "provider": args.provider,
        "model": args.model,
        "policy_no_claude_provider": True,
        "sandbox_mode": args.sandbox,
        "approval_policy": args.approval,
        "dry_run": bool(args.dry_run),
        "operator": args.operator,
        "tasks_source": str(tasks_path),
        "tasks_copied_to": "tasks.jsonl",
        "results_file": "results.jsonl",
        "agent_events_file": "agent_events.jsonl",
    }

    with (run_dir / "run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
