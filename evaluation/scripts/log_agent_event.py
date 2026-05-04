#!/usr/bin/env python3
"""
Append one normalized agent event row to a run.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUS = {"started", "running", "completed", "failed", "blocked", "skipped"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log one agent activity event.")
    parser.add_argument("--run-dir", required=True, help="Path to one run directory.")
    parser.add_argument("--scenario-id", required=True, help="Scenario id, e.g. S001.")
    parser.add_argument("--agent-id", required=True, help="Stable agent id.")
    parser.add_argument("--agent-role", required=True, help="Agent role or specialization.")
    parser.add_argument("--what", required=True, help="What was done.")
    parser.add_argument("--where", required=True, help="Where it happened (file/path/module).")
    parser.add_argument("--why", required=True, help="Why the action was taken.")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUS), help="Event status.")
    parser.add_argument("--start-ms", type=int, required=True, help="Start offset in ms from run start.")
    parser.add_argument("--duration-ms", type=int, required=True, help="Duration in ms.")
    parser.add_argument("--tokens-prompt", type=int, default=0, help="Prompt/input tokens.")
    parser.add_argument("--tokens-completion", type=int, default=0, help="Completion/output tokens.")
    parser.add_argument("--tokens-cached", type=int, default=0, help="Cached tokens.")
    parser.add_argument("--notes", default=None, help="Optional note.")
    return parser.parse_args()


def load_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    if args.start_ms < 0 or args.duration_ms < 0:
        raise ValueError("--start-ms and --duration-ms must be >= 0")

    if args.tokens_prompt < 0 or args.tokens_completion < 0 or args.tokens_cached < 0:
        raise ValueError("token values must be >= 0")

    manifest = load_manifest(run_dir)
    out_path = run_dir / "agent_events.jsonl"
    if not out_path.exists():
        out_path.write_text("", encoding="utf-8")

    record = {
        "record_version": 1,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": manifest.get("run_id"),
        "scenario_id": args.scenario_id,
        "agent_id": args.agent_id,
        "agent_role": args.agent_role,
        "what": args.what,
        "where": args.where,
        "why": args.why,
        "status": args.status,
        "start_ms": args.start_ms,
        "duration_ms": args.duration_ms,
        "tokens_prompt": args.tokens_prompt,
        "tokens_completion": args.tokens_completion,
        "tokens_cached": args.tokens_cached,
        "tokens_total": args.tokens_prompt + args.tokens_completion + args.tokens_cached,
        "notes": args.notes,
    }

    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True))
        f.write("\n")

    print(json.dumps({"ok": True, "run_dir": str(run_dir), "agent_id": args.agent_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
