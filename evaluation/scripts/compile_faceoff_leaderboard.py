#!/usr/bin/env python3
"""
Compile a faceoff leaderboard from competitor run directories.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile faceoff leaderboard.")
    parser.add_argument("--round-dir", required=True, help="Round directory created by bootstrap script.")
    parser.add_argument("--codex-run-dir", default=None, help="Run directory for codex.")
    parser.add_argument("--gemini-run-dir", default=None, help="Run directory for gemini.")
    parser.add_argument("--ollama-run-dir", default=None, help="Run directory for ollama.")
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
            if raw:
                rows.append(json.loads(raw))
    return rows


def clamp_0_5(value: float | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(5.0, float(value)))


def collect_metrics(run_dir: Path) -> dict:
    manifest = read_json(run_dir / "run_manifest.json")
    results = read_jsonl(run_dir / "results.jsonl")

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "pass")
    hard_fail = sum(1 for r in results if r.get("status") in {"fail", "error", "blocked"})
    durations = [float(r.get("duration_ms", 0)) for r in results]
    tokens = [float(r.get("tokens_total", 0)) for r in results]
    quality = [float(r.get("quality_score")) for r in results if r.get("quality_score") is not None]
    interventions = sum(int(r.get("human_interventions", 0)) for r in results)

    success_rate = (passed / total * 100.0) if total else 0.0
    hard_fail_rate = (hard_fail / total * 100.0) if total else 0.0
    speed_tasks_per_hour = (total / sum(durations) * 3600000.0) if sum(durations) else 0.0
    avg_tokens = (sum(tokens) / total) if total else 0.0
    avg_quality = (sum(quality) / len(quality)) if quality else 0.0
    intervention_rate = (interventions / total * 100.0) if total else 0.0
    median_duration_ms = statistics.median(durations) if durations else 0.0

    return {
        "run_dir": str(run_dir),
        "provider": manifest.get("provider", "unknown"),
        "model": manifest.get("model", "unknown"),
        "total_tasks": total,
        "success_rate_pct": success_rate,
        "hard_failure_rate_pct": hard_fail_rate,
        "speed_tasks_per_hour": speed_tasks_per_hour,
        "avg_tokens_per_task": avg_tokens,
        "avg_quality_0_to_5": avg_quality,
        "intervention_rate_pct": intervention_rate,
        "median_duration_ms": median_duration_ms,
    }


def normalize(values: list[float], higher_is_better: bool) -> list[float]:
    if not values:
        return []
    vmin = min(values)
    vmax = max(values)
    if vmax == vmin:
        return [1.0 for _ in values]
    if higher_is_better:
        return [(v - vmin) / (vmax - vmin) for v in values]
    return [(vmax - v) / (vmax - vmin) for v in values]


def competitor_name(provider: str) -> str:
    p = provider.strip().lower()
    if "codex" in p:
        return "codex"
    if "gemini" in p:
        return "gemini"
    if "ollama" in p:
        return "ollama"
    return p


def load_manual_scores(round_dir: Path, competitor: str) -> dict:
    path = round_dir / "submissions" / competitor / "SUBMISSION_METRICS.json"
    if not path.exists():
        return {}
    return read_json(path)


def load_credits(round_dir: Path, competitor: str) -> dict:
    path = round_dir / "submissions" / competitor / "CREDITS.json"
    if not path.exists():
        return {}
    return read_json(path)


def count_markdown_bullets(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- ") or s.startswith("* "):
                item = s[2:].strip()
                if item.startswith("[ ]"):
                    continue
                count += 1
    return count


def main() -> int:
    args = parse_args()
    round_dir = Path(args.round_dir)
    manifest = read_json(round_dir / "round_manifest.json")

    run_paths = []
    for maybe in [args.codex_run_dir, args.gemini_run_dir, args.ollama_run_dir]:
        if maybe:
            run_paths.append(Path(maybe))

    entries: list[dict] = []
    for run_dir in run_paths:
        metrics = collect_metrics(run_dir)
        competitor = competitor_name(metrics["provider"])
        manual = load_manual_scores(round_dir, competitor)
        credits = load_credits(round_dir, competitor)
        improvements_count = count_markdown_bullets(
            round_dir / "submissions" / competitor / "SYSTEM_IMPROVEMENTS.md"
        )
        innovations_count = count_markdown_bullets(
            round_dir / "submissions" / competitor / "INNOVATIONS.md"
        )
        breakthroughs_count = count_markdown_bullets(
            round_dir / "submissions" / competitor / "BREAKTHROUGHS.md"
        )
        metrics["competitor"] = competitor
        metrics["improvement_proposals_count"] = improvements_count
        metrics["innovation_items_count"] = innovations_count
        metrics["breakthrough_items_count"] = breakthroughs_count
        metrics["human_contributor_count"] = len(credits.get("human_contributors", []) or [])
        metrics["agent_contributor_count"] = len(credits.get("agent_contributors", []) or [])
        metrics["manual"] = {
            "engagement_score_0_to_5": clamp_0_5(manual.get("engagement_score_0_to_5")),
            "usefulness_score_0_to_5": clamp_0_5(manual.get("usefulness_score_0_to_5")),
            "observability_clarity_0_to_5": clamp_0_5(manual.get("observability_clarity_0_to_5")),
            "novelty_score_0_to_5": clamp_0_5(manual.get("novelty_score_0_to_5")),
            "open_standards_score_0_to_5": clamp_0_5(manual.get("open_standards_score_0_to_5")),
            "open_source_contribution_score_0_to_5": clamp_0_5(manual.get("open_source_contribution_score_0_to_5")),
            "breakthrough_score_0_to_5": clamp_0_5(manual.get("breakthrough_score_0_to_5")),
            "peer_votes": int(manual.get("peer_votes", 0) or 0),
            "citation_count": len(manual.get("citations", []) or []),
            "collaboration_link_count": len(manual.get("collaboration_links", []) or []),
            "github_handles": manual.get("github_handles", []) or [],
            "x_handles": manual.get("x_handles", []) or [],
            "open_source_links": manual.get("open_source_links", []) or [],
            "notes": str(manual.get("notes", "")),
        }
        entries.append(metrics)

    if not entries:
        raise ValueError("No competitor run dirs provided.")

    success_vals = [e["success_rate_pct"] for e in entries]
    quality_vals = [e["avg_quality_0_to_5"] for e in entries]
    speed_vals = [e["speed_tasks_per_hour"] for e in entries]
    token_vals = [e["avg_tokens_per_task"] for e in entries]
    observability_vals = [e["manual"]["observability_clarity_0_to_5"] for e in entries]
    engagement_vals = [
        (e["manual"]["engagement_score_0_to_5"] + e["manual"]["usefulness_score_0_to_5"]) / 2.0 for e in entries
    ]
    novelty_vals = [e["manual"]["novelty_score_0_to_5"] for e in entries]

    success_n = normalize(success_vals, higher_is_better=True)
    quality_n = normalize(quality_vals, higher_is_better=True)
    speed_n = normalize(speed_vals, higher_is_better=True)
    token_n = normalize(token_vals, higher_is_better=False)
    observability_n = normalize(observability_vals, higher_is_better=True)
    engagement_n = normalize(engagement_vals, higher_is_better=True)
    novelty_n = normalize(novelty_vals, higher_is_better=True)

    weights = manifest.get("scoring_weights", {})
    bonus_max = float(
        manifest.get("bonus_policy", {}).get("open_standards_and_open_source_max_points", 10)
    )
    breakthrough_bonus_max = float(
        manifest.get("bonus_policy", {}).get("breakthrough_discovery_max_points", 10)
    )
    scored: list[dict] = []
    for i, entry in enumerate(entries):
        base_score = (
            weights.get("reliability_success_rate", 0.20) * success_n[i]
            + weights.get("intelligence_quality", 0.20) * quality_n[i]
            + weights.get("speed_tasks_per_hour", 0.15) * speed_n[i]
            + weights.get("efficiency_tokens_inverse", 0.15) * token_n[i]
            + weights.get("observability_clarity", 0.10) * observability_n[i]
            + weights.get("engagement_usefulness", 0.10) * engagement_n[i]
            + weights.get("novelty", 0.10) * novelty_n[i]
        )
        m = entry["manual"]
        bonus_ratio = (m["open_standards_score_0_to_5"] + m["open_source_contribution_score_0_to_5"]) / 10.0
        bonus_score = bonus_ratio * bonus_max
        breakthrough_bonus = (m["breakthrough_score_0_to_5"] / 5.0) * breakthrough_bonus_max
        citation_bonus = min(5.0, float(m["citation_count"]) * 0.5)
        collaboration_bonus = min(5.0, float(m["collaboration_link_count"]) * 0.5)
        peer_bonus = min(5.0, float(m["peer_votes"]) * 0.2)
        merit_bonus = citation_bonus + collaboration_bonus + peer_bonus
        entry["total_score_0_to_100"] = round(base_score * 100.0, 2)
        entry["bonus_score"] = round(bonus_score, 2)
        entry["breakthrough_bonus_score"] = round(breakthrough_bonus, 2)
        entry["merit_bonus_score"] = round(merit_bonus, 2)
        entry["final_score"] = round(
            entry["total_score_0_to_100"]
            + entry["bonus_score"]
            + entry["breakthrough_bonus_score"]
            + entry["merit_bonus_score"],
            2,
        )
        scored.append(entry)

    scored.sort(key=lambda e: e["final_score"], reverse=True)
    for rank, entry in enumerate(scored, start=1):
        entry["rank"] = rank

    results_dir = round_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    leaderboard_json = {
        "round_id": manifest.get("round_id"),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entries": scored,
    }
    (results_dir / "leaderboard.json").write_text(json.dumps(leaderboard_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# Leaderboard")
    lines.append("")
    lines.append(f"Round: `{manifest.get('round_id')}`")
    lines.append("")
    lines.append(
        "| Rank | Competitor | Base | Open/OSS Bonus | Breakthrough Bonus | Merit Bonus | Final | Success % | Speed tasks/hr | Avg Tokens | Intelligence | Obs Clarity | Engagement | Novelty | Citations | Collabs | Peer Votes | Humans | Agents | Improvements | Innovations | Breakthroughs | Run Dir |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for e in scored:
        m = e["manual"]
        engagement = (m["engagement_score_0_to_5"] + m["usefulness_score_0_to_5"]) / 2.0
        lines.append(
            f"| {e['rank']} | {e['competitor']} | {e['total_score_0_to_100']:.2f} | "
            f"{e['bonus_score']:.2f} | {e['breakthrough_bonus_score']:.2f} | {e['merit_bonus_score']:.2f} | {e['final_score']:.2f} | "
            f"{e['success_rate_pct']:.2f} | {e['speed_tasks_per_hour']:.2f} | {e['avg_tokens_per_task']:.0f} | "
            f"{e['avg_quality_0_to_5']:.2f} | {m['observability_clarity_0_to_5']:.2f} | "
            f"{engagement:.2f} | {m['novelty_score_0_to_5']:.2f} | "
            f"{m['citation_count']} | {m['collaboration_link_count']} | {m['peer_votes']} | "
            f"{e['human_contributor_count']} | {e['agent_contributor_count']} | "
            f"{e['improvement_proposals_count']} | {e['innovation_items_count']} | {e['breakthrough_items_count']} | `{e['run_dir']}` |"
        )

    winner = scored[0]
    lines.append("")
    lines.append(
        f"Winner: `{winner['competitor']}` with final score `{winner['final_score']:.2f}` "
        f"(base `{winner['total_score_0_to_100']:.2f}` + open/oss bonus `{winner['bonus_score']:.2f}` + breakthrough bonus `{winner['breakthrough_bonus_score']:.2f}` + merit bonus `{winner['merit_bonus_score']:.2f}`)."
    )
    lines.append("")
    lines.append("Next: generate highlight replay from winner and challenger bird's-eye timelines.")
    (results_dir / "leaderboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(results_dir / "leaderboard.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
