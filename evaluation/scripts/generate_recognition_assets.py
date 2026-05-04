#!/usr/bin/env python3
"""
Generate meritocracy recognition assets from a round leaderboard.
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate recognition assets for one faceoff round.")
    parser.add_argument("--round-dir", required=True, help="Round directory path.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def badge(label: str, message: str, color: str) -> str:
    l = urllib.parse.quote(label)
    m = urllib.parse.quote(message)
    c = urllib.parse.quote(color)
    return f"https://img.shields.io/badge/{l}-{m}-{c}"


def clean_handle(handle: str) -> str:
    h = handle.strip()
    if h.startswith("@"):
        return h
    return f"@{h}" if h else h


def main() -> int:
    args = parse_args()
    round_dir = Path(args.round_dir)
    leaderboard_path = round_dir / "results" / "leaderboard.json"
    round_manifest_path = round_dir / "round_manifest.json"

    if not leaderboard_path.exists():
        raise FileNotFoundError(f"Missing leaderboard: {leaderboard_path}")

    leaderboard = read_json(leaderboard_path)
    round_manifest = read_json(round_manifest_path)
    entries = leaderboard.get("entries", [])
    round_id = round_manifest.get("round_id", round_dir.name)

    results_dir = round_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    recognition_entries = []
    md_lines: list[str] = []
    md_lines.append("# Recognition Registry")
    md_lines.append("")
    md_lines.append(f"Round: `{round_id}`")
    md_lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
    md_lines.append("")
    md_lines.append(
        "| Rank | Competitor | Final | Merit Bonus | Citations | Collabs | Peer Votes | Humans | Agents | GitHub Handles | X Handles |"
    )
    md_lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|")

    badge_lines: list[str] = []
    badge_lines.append("# GitHub Badge Snippets")
    badge_lines.append("")

    social_lines: list[str] = []
    social_lines.append("# Social Post Templates")
    social_lines.append("")

    citation_nodes = {}
    citation_edges = []

    for e in entries:
        m = e.get("manual", {}) or {}
        github_handles = [clean_handle(h) for h in (m.get("github_handles", []) or []) if str(h).strip()]
        x_handles = [clean_handle(h) for h in (m.get("x_handles", []) or []) if str(h).strip()]
        citations = m.get("citations", []) or []
        collabs = m.get("collaboration_links", []) or []

        rec = {
            "round_id": round_id,
            "rank": e.get("rank"),
            "competitor": e.get("competitor"),
            "final_score": e.get("final_score"),
            "merit_bonus_score": e.get("merit_bonus_score"),
            "citation_count": m.get("citation_count", 0),
            "collaboration_link_count": m.get("collaboration_link_count", 0),
            "peer_votes": m.get("peer_votes", 0),
            "human_contributor_count": e.get("human_contributor_count", 0),
            "agent_contributor_count": e.get("agent_contributor_count", 0),
            "github_handles": github_handles,
            "x_handles": x_handles,
            "run_dir": e.get("run_dir"),
        }
        recognition_entries.append(rec)

        md_lines.append(
            f"| {rec['rank']} | {rec['competitor']} | {rec['final_score']} | {rec['merit_bonus_score']} | "
            f"{rec['citation_count']} | {rec['collaboration_link_count']} | {rec['peer_votes']} | "
            f"{rec['human_contributor_count']} | {rec['agent_contributor_count']} | "
            f"{', '.join(github_handles) if github_handles else '-'} | {', '.join(x_handles) if x_handles else '-'} |"
        )

        rank_badge = badge("rank", str(rec["rank"]), "blue")
        final_badge = badge("final_score", f"{rec['final_score']}", "brightgreen")
        merit_badge = badge("merit_bonus", f"{rec['merit_bonus_score']}", "orange")
        breakthrough_badge = badge("breakthrough_bonus", f"{e.get('breakthrough_bonus_score', 0)}", "purple")

        badge_lines.append(f"## {rec['competitor']}")
        badge_lines.append("")
        badge_lines.append(f"![rank]({rank_badge}) ![final]({final_badge}) ![merit]({merit_badge}) ![breakthrough]({breakthrough_badge})")
        badge_lines.append("")
        badge_lines.append("```md")
        badge_lines.append(f"![rank]({rank_badge})")
        badge_lines.append(f"![final]({final_badge})")
        badge_lines.append(f"![merit]({merit_badge})")
        badge_lines.append(f"![breakthrough]({breakthrough_badge})")
        badge_lines.append("```")
        badge_lines.append("")

        tags = " ".join(x_handles[:4]) if x_handles else ""
        social_lines.append(f"## {rec['competitor']}")
        social_lines.append("")
        social_lines.append(
            f"Round {round_id}: {rec['competitor']} ranked #{rec['rank']} "
            f"with final score {rec['final_score']} (merit bonus {rec['merit_bonus_score']}). "
            f"Citations={rec['citation_count']} Collabs={rec['collaboration_link_count']} "
            f"#SimulationFaceoff #OpenSource #AIEngineering {tags}".strip()
        )
        social_lines.append("")

        src = rec["competitor"]
        citation_nodes[src] = {"id": src, "type": "competitor"}
        for c in citations:
            target = str(c).strip()
            if not target:
                continue
            citation_nodes[target] = {"id": target, "type": "citation_target"}
            citation_edges.append({"source": src, "target": target, "kind": "citation"})

    registry = {
        "round_id": round_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entries": recognition_entries,
    }
    (results_dir / "recognition_registry.json").write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    (results_dir / "recognition_registry.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    (results_dir / "github_badges.md").write_text("\n".join(badge_lines) + "\n", encoding="utf-8")
    (results_dir / "social_posts.md").write_text("\n".join(social_lines) + "\n", encoding="utf-8")

    citation_graph = {
        "round_id": round_id,
        "nodes": list(citation_nodes.values()),
        "edges": citation_edges,
    }
    (results_dir / "citation_graph.json").write_text(
        json.dumps(citation_graph, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(str(results_dir / "recognition_registry.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
