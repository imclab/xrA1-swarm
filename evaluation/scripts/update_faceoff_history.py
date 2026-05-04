#!/usr/bin/env python3
"""
Aggregate all faceoff rounds into a persistent history log and report.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update faceoff history report from all round leaderboards.")
    parser.add_argument("--rounds-root", default="evaluation/faceoff_rounds", help="Root folder of faceoff rounds.")
    parser.add_argument("--write-jsonl", default="evaluation/reports/faceoff_history.jsonl", help="History jsonl output.")
    parser.add_argument("--write-markdown", default="evaluation/reports/faceoff_history.md", help="History markdown output.")
    parser.add_argument(
        "--write-innovation-backlog",
        default="evaluation/reports/innovation_backlog.md",
        help="Aggregated innovation/improvement backlog markdown output.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_bullets(path: Path) -> list[str]:
    if not path.exists():
        return []
    items: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- ") or s.startswith("* "):
                item = s[2:].strip()
                if item.startswith("[ ]"):
                    continue
                items.append(item)
    return items


def main() -> int:
    args = parse_args()
    rounds_root = Path(args.rounds_root)
    entries: list[dict] = []
    backlog_rows: list[dict] = []

    if rounds_root.exists():
        for round_dir in sorted([p for p in rounds_root.iterdir() if p.is_dir()]):
            manifest_path = round_dir / "round_manifest.json"
            leaderboard_path = round_dir / "results" / "leaderboard.json"
            if not manifest_path.exists() or not leaderboard_path.exists():
                continue

            manifest = read_json(manifest_path)
            leaderboard = read_json(leaderboard_path)
            lb_entries = leaderboard.get("entries", [])
            if not lb_entries:
                continue

            winner = lb_entries[0].get("competitor", "unknown")
            entries.append(
                {
                    "record_version": 1,
                    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "round_id": manifest.get("round_id", round_dir.name),
                    "winner": winner,
                    "entries": [
                        {
                            "rank": e.get("rank"),
                            "competitor": e.get("competitor"),
                            "score_0_to_100": e.get("total_score_0_to_100"),
                            "open_oss_bonus_score": e.get("bonus_score", 0),
                            "breakthrough_bonus_score": e.get("breakthrough_bonus_score", 0),
                            "merit_bonus_score": e.get("merit_bonus_score", 0),
                            "final_score": e.get("final_score", e.get("total_score_0_to_100")),
                            "success_rate_pct": e.get("success_rate_pct"),
                            "speed_tasks_per_hour": e.get("speed_tasks_per_hour"),
                            "avg_tokens_per_task": e.get("avg_tokens_per_task"),
                            "avg_quality_0_to_5": e.get("avg_quality_0_to_5"),
                            "human_contributor_count": e.get("human_contributor_count", 0),
                            "agent_contributor_count": e.get("agent_contributor_count", 0),
                            "citation_count": (e.get("manual", {}) or {}).get("citation_count", 0),
                            "collaboration_link_count": (e.get("manual", {}) or {}).get("collaboration_link_count", 0),
                            "peer_votes": (e.get("manual", {}) or {}).get("peer_votes", 0),
                            "improvement_proposals_count": e.get("improvement_proposals_count", 0),
                            "innovation_items_count": e.get("innovation_items_count", 0),
                            "breakthrough_items_count": e.get("breakthrough_items_count", 0),
                            "run_dir": e.get("run_dir"),
                        }
                        for e in lb_entries
                    ],
                }
            )

            submissions_dir = round_dir / "submissions"
            if submissions_dir.exists():
                for competitor_dir in sorted([p for p in submissions_dir.iterdir() if p.is_dir()]):
                    competitor = competitor_dir.name
                    improvements = read_bullets(competitor_dir / "SYSTEM_IMPROVEMENTS.md")
                    innovations = read_bullets(competitor_dir / "INNOVATIONS.md")
                    for item in improvements:
                        backlog_rows.append(
                            {
                                "round_id": manifest.get("round_id", round_dir.name),
                                "competitor": competitor,
                                "type": "improvement",
                                "text": item,
                            }
                        )
                    for item in innovations:
                        backlog_rows.append(
                            {
                                "round_id": manifest.get("round_id", round_dir.name),
                                "competitor": competitor,
                                "type": "innovation",
                                "text": item,
                            }
                        )
                    breakthroughs = read_bullets(competitor_dir / "BREAKTHROUGHS.md")
                    for item in breakthroughs:
                        backlog_rows.append(
                            {
                                "round_id": manifest.get("round_id", round_dir.name),
                                "competitor": competitor,
                                "type": "breakthrough",
                                "text": item,
                            }
                        )

    jsonl_path = Path(args.write_jsonl)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in entries:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")

    md_lines: list[str] = []
    md_lines.append("# Faceoff History")
    md_lines.append("")
    md_lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
    md_lines.append("")
    md_lines.append("| Round | Winner | Competitors |")
    md_lines.append("|---|---|---|")
    for row in entries:
        competitors = ", ".join(
            [f"{e.get('rank')}. {e.get('competitor')} ({e.get('final_score')})" for e in row.get("entries", [])]
        )
        md_lines.append(f"| {row.get('round_id')} | {row.get('winner')} | {competitors} |")
    if not entries:
        md_lines.append("| - | - | No completed leaderboards found |")
    md_lines.append("")

    md_path = Path(args.write_markdown)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    backlog_lines: list[str] = []
    backlog_lines.append("# Innovation Backlog")
    backlog_lines.append("")
    backlog_lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
    backlog_lines.append("")
    backlog_lines.append("| Round | Competitor | Type | Item |")
    backlog_lines.append("|---|---|---|---|")
    if backlog_rows:
        for row in backlog_rows:
            backlog_lines.append(
                f"| {row['round_id']} | {row['competitor']} | {row['type']} | {row['text']} |"
            )
    else:
        backlog_lines.append("| - | - | - | No innovation/improvement items found |")
    backlog_lines.append("")

    backlog_path = Path(args.write_innovation_backlog)
    backlog_path.parent.mkdir(parents=True, exist_ok=True)
    backlog_path.write_text("\n".join(backlog_lines) + "\n", encoding="utf-8")

    print(str(md_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
