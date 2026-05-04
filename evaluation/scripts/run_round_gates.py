#!/usr/bin/env python3
"""
Run checkpoint gates for a round over the 10-minute window.

Default milestones:
- start gate at T-09:00 (1 min elapsed)
- kickoff gate at T-08:00 (2 min elapsed)
- halfway gate at T-05:00
- midpush gate at T-04:00
- final gate at T-00:00
"""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run timed round gates.")
    parser.add_argument("--round-dir", required=True, help="Round directory path.")
    parser.add_argument("--minutes", type=int, default=10, help="Total round duration.")
    parser.add_argument("--start-elapsed-sec", type=int, default=60, help="Start gate elapsed seconds.")
    parser.add_argument("--kickoff-elapsed-sec", type=int, default=120, help="Kickoff gate elapsed seconds.")
    parser.add_argument("--halfway-elapsed-sec", type=int, default=300, help="Halfway gate elapsed seconds.")
    parser.add_argument("--midpush-elapsed-sec", type=int, default=360, help="Midpush gate elapsed seconds.")
    parser.add_argument("--tick-sec", type=float, default=1.0, help="Timer poll interval.")
    return parser.parse_args()


def run_gate(round_dir: Path, checkpoint: str) -> int:
    cmd = [
        "python3",
        "evaluation/scripts/validate_final_outputs.py",
        "--round-dir",
        str(round_dir),
        "--checkpoint",
        checkpoint,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    print(f"[GATE:{checkpoint}] exit={proc.returncode}")
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip())
    return proc.returncode


def main() -> int:
    args = parse_args()
    round_dir = Path(args.round_dir)
    total = max(1, int(args.minutes) * 60)
    start = max(1, int(args.start_elapsed_sec))
    kickoff = max(1, int(args.kickoff_elapsed_sec))
    halfway = max(1, int(args.halfway_elapsed_sec))
    midpush = max(1, int(args.midpush_elapsed_sec))

    fired = {"start": False, "kickoff": False, "halfway": False, "midpush": False, "final": False}
    started_at = time.time()
    print(
        f"[GATE] round={round_dir} total={total}s "
        f"milestones=start@{start}s kickoff@{kickoff}s halfway@{halfway}s midpush@{midpush}s final@{total}s"
    )

    while True:
        elapsed = int(time.time() - started_at)
        if not fired["start"] and elapsed >= start:
            fired["start"] = True
            run_gate(round_dir, "start")
        if not fired["kickoff"] and elapsed >= kickoff:
            fired["kickoff"] = True
            run_gate(round_dir, "kickoff")
        if not fired["halfway"] and elapsed >= halfway:
            fired["halfway"] = True
            run_gate(round_dir, "halfway")
        if not fired["midpush"] and elapsed >= midpush:
            fired["midpush"] = True
            run_gate(round_dir, "midpush")
        if elapsed >= total:
            if not fired["final"]:
                fired["final"] = True
                run_gate(round_dir, "final")
            break
        time.sleep(max(0.01, float(args.tick_sec)))

    print("[GATE] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
