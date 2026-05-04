#!/usr/bin/env python3
"""
Round countdown utility for CI/terminal and local sessions.

Prints clear cue markers at:
- start
- halfway
- final 3 minutes
- final 30/10 seconds
- buzzer
"""

from __future__ import annotations

import argparse
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a countdown timer with milestone cues.")
    parser.add_argument("--minutes", type=int, default=10, help="Countdown duration in minutes (default: 10).")
    parser.add_argument(
        "--tick-seconds",
        type=float,
        default=1.0,
        help="Tick interval in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--label",
        default="FACEOFF",
        help="Prefix label in logs.",
    )
    parser.add_argument(
        "--fast-demo",
        action="store_true",
        help="Demo mode: compresses each minute to 1 second for quick verification.",
    )
    return parser.parse_args()


def fmt(secs: int) -> str:
    mm = secs // 60
    ss = secs % 60
    return f"{mm:02d}:{ss:02d}"


def main() -> int:
    args = parse_args()
    total_secs = max(1, args.minutes * 60)
    step = max(0.01, float(args.tick_seconds))

    if args.fast_demo:
        total_secs = max(1, args.minutes)
        step = 1.0

    half = total_secs // 2
    final_three = min(total_secs, 180 if not args.fast_demo else 3)

    print(f"[{args.label}] START | countdown={fmt(total_secs)}")
    print(f"[{args.label}] CUE_START | Launch now. Ship before buzzer.")

    last_print = None
    for elapsed in range(0, total_secs + 1):
        remaining = total_secs - elapsed
        if remaining != last_print and (remaining % 30 == 0 or remaining <= 10):
            print(f"[{args.label}] T-{fmt(remaining)}")
            last_print = remaining

        if remaining == half:
            print(f"[{args.label}] CUE_HALF | Halfway checkpoint.")
        if remaining == final_three:
            print(f"[{args.label}] CUE_FINAL_THREE | Final stretch begins.")
        if remaining == (30 if not args.fast_demo else 1):
            print(f"[{args.label}] CUE_FINAL_30S | Wrap immediately.")
        if remaining == (10 if not args.fast_demo else 1):
            print(f"[{args.label}] CUE_FINAL_10S | Final commit now.")

        if remaining == 0:
            break
        time.sleep(step)

    print(f"[{args.label}] BUZZER | Time is up. Submit current state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
