#!/usr/bin/env python3
"""
Validate final game/simulation outputs for a faceoff round.

Checkpoints:
- kickoff: early proof of implementation movement.
- halfway: playable web + meaningful docs + Unity path progress.
- final: strict ship gate for leaderboard eligibility.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


COMPETITORS = ("codex", "gemini", "ollama")
VALID_FINAL_STATUS = {"ready", "complete", "submitted"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate round final output requirements.")
    parser.add_argument("--round-dir", required=True, help="Round directory path.")
    parser.add_argument(
        "--checkpoint",
        default="final",
        choices=["kickoff", "halfway", "final"],
        help="Validation strictness profile.",
    )
    parser.add_argument("--competitor", action="append", default=[], help="Optional competitor filter.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def looks_placeholder_markdown(path: Path) -> bool:
    if not path.exists():
        return True
    text = read_text(path).strip()
    if not text:
        return True
    if "- [ ]" in text:
        return True
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Header-only or near-empty template text is not acceptable as "done".
    if len(lines) <= 2:
        return True
    return False


def resolve_path(base: Path, raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    return base / p


def validate_competitor(round_dir: Path, competitor: str, checkpoint: str) -> dict:
    sub_dir = round_dir / "submissions" / competitor
    manifest_path = sub_dir / "FINAL_OUTPUT_MANIFEST.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}

    web_rel = str(manifest.get("web_entrypoint", "final_game/web/index.html"))
    unity_rel = str(manifest.get("unity_build_info", "final_game/unity/UNITY_BUILD_INFO.json"))
    web_path = resolve_path(sub_dir, web_rel)
    unity_info_path = resolve_path(sub_dir, unity_rel)

    web_exists = web_path.exists() and web_path.is_file() and web_path.stat().st_size > 0
    unity_info = read_json(unity_info_path) if unity_info_path.exists() else {}
    unity_info_exists = unity_info_path.exists() and unity_info_path.is_file() and unity_info_path.stat().st_size > 0

    unity_project_raw = str(manifest.get("unity_project_path") or unity_info.get("project_path") or "").strip()
    unity_build_raw = str(manifest.get("unity_build_path") or unity_info.get("build_path") or "").strip()
    unity_project_path = resolve_path(sub_dir, unity_project_raw) if unity_project_raw else None
    unity_build_path = resolve_path(sub_dir, unity_build_raw) if unity_build_raw else None
    unity_project_exists = bool(unity_project_path and unity_project_path.exists())
    unity_build_exists = bool(unity_build_path and unity_build_path.exists())

    status = str(manifest.get("status", "")).strip().lower()
    unity_status = str(unity_info.get("status", "")).strip().lower()

    system_md = sub_dir / "SYSTEM.md"
    runbook_md = sub_dir / "RUNBOOK.md"
    artifacts_md = sub_dir / "ARTIFACTS.md"

    missing: list[str] = []
    checks: list[str] = []

    if checkpoint == "kickoff":
        checks.extend(
            [
                "final manifest exists",
                "web index exists",
                "manifest status in_progress/ready/complete/submitted",
            ]
        )
        if not manifest_path.exists():
            missing.append("missing_FINAL_OUTPUT_MANIFEST.json")
        if not web_exists:
            missing.append(f"missing_web_entrypoint:{web_rel}")
        if status not in {"in_progress", "ready", "complete", "submitted"}:
            missing.append("manifest_status_not_started")

    elif checkpoint == "halfway":
        checks.extend(
            [
                "web index exists",
                "unity info exists with progress path",
                "SYSTEM/RUNBOOK/ARTIFACTS not placeholders",
            ]
        )
        if not web_exists:
            missing.append(f"missing_web_entrypoint:{web_rel}")
        if not unity_info_exists:
            missing.append(f"missing_unity_build_info:{unity_rel}")
        if unity_info_exists and not (unity_project_raw or unity_build_raw):
            missing.append("unity_project_or_build_path_empty")
        if looks_placeholder_markdown(system_md):
            missing.append("SYSTEM.md_incomplete")
        if looks_placeholder_markdown(runbook_md):
            missing.append("RUNBOOK.md_incomplete")
        if looks_placeholder_markdown(artifacts_md):
            missing.append("ARTIFACTS.md_incomplete")

    else:  # final
        checks.extend(
            [
                "web index exists",
                "unity build info exists",
                "unity project/build path exists",
                "SYSTEM/RUNBOOK/ARTIFACTS complete",
                "manifest + unity status final",
            ]
        )
        if not web_exists:
            missing.append(f"missing_web_entrypoint:{web_rel}")
        if not unity_info_exists:
            missing.append(f"missing_unity_build_info:{unity_rel}")
        if unity_info_exists and not (unity_project_exists or unity_build_exists):
            missing.append("unity_project_or_build_path_missing_on_disk")
        if looks_placeholder_markdown(system_md):
            missing.append("SYSTEM.md_incomplete")
        if looks_placeholder_markdown(runbook_md):
            missing.append("RUNBOOK.md_incomplete")
        if looks_placeholder_markdown(artifacts_md):
            missing.append("ARTIFACTS.md_incomplete")
        if status not in VALID_FINAL_STATUS:
            missing.append("manifest_status_not_final")
        if unity_status and unity_status not in VALID_FINAL_STATUS:
            missing.append("unity_status_not_final")

    passed = len(missing) == 0
    return {
        "competitor": competitor,
        "checkpoint": checkpoint,
        "checks": checks,
        "passed": passed,
        "missing": missing,
        "web_entrypoint": str(web_path),
        "unity_info_path": str(unity_info_path),
        "unity_project_path": str(unity_project_path) if unity_project_path else "",
        "unity_build_path": str(unity_build_path) if unity_build_path else "",
    }


def main() -> int:
    args = parse_args()
    round_dir = Path(args.round_dir)
    competitors = args.competitor if args.competitor else list(COMPETITORS)

    results = [validate_competitor(round_dir, c, args.checkpoint) for c in competitors]
    all_passed = all(r["passed"] for r in results)

    if args.json:
        print(json.dumps({"round_dir": str(round_dir), "checkpoint": args.checkpoint, "passed": all_passed, "results": results}, indent=2))
    else:
        print(f"Round: {round_dir}")
        print(f"Checkpoint: {args.checkpoint}")
        print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
        for r in results:
            print(f"- {r['competitor']}: {'PASS' if r['passed'] else 'FAIL'}")
            if r["missing"]:
                for m in r["missing"]:
                    print(f"  - {m}")

    return 0 if all_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
