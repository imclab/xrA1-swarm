#!/usr/bin/env python3
"""
Build a static faceoff site from evaluation round artifacts.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build static faceoff site from round artifacts.")
    parser.add_argument("--rounds-root", default="evaluation/faceoff_rounds", help="Round artifact root.")
    parser.add_argument("--site-root", default="docs/faceoff", help="Output site root.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def copy_if_exists(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree_if_exists(src: Path, dst: Path) -> None:
    if not src.exists() or not src.is_dir():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def build_round_pages(round_dir: Path, out_round_dir: Path) -> dict:
    round_manifest = read_json(round_dir / "round_manifest.json")
    round_id = round_manifest.get("round_id", round_dir.name)
    results_dir = round_dir / "results"
    out_results_dir = out_round_dir / "results"
    out_results_dir.mkdir(parents=True, exist_ok=True)

    copied_results: set[str] = set()
    for f in [
        "leaderboard.md",
        "leaderboard.json",
        "recognition_registry.md",
        "recognition_registry.json",
        "github_badges.md",
        "social_posts.md",
        "citation_graph.json",
        "countdown_demo.log",
        "codex_birdseye.html",
        "gemini_birdseye.html",
        "ollama_birdseye.html",
        "codex_final_report.md",
        "gemini_final_report.md",
        "ollama_final_report.md",
    ]:
        src = results_dir / f
        if src.exists():
            copy_if_exists(src, out_results_dir / f)
            copied_results.add(f)

    copy_if_exists(round_dir / "execution_plan.md", out_round_dir / "execution_plan.md")
    copy_if_exists(round_dir / "round_manifest.json", out_round_dir / "round_manifest.json")

    competitors = round_manifest.get("competitors", ["codex", "gemini", "ollama"])
    published_games: dict[str, dict[str, str | bool]] = {}
    for competitor in competitors:
        c = str(competitor)
        sub_dir = round_dir / "submissions" / c
        out_sub_dir = out_round_dir / "submissions" / c
        copy_if_exists(sub_dir / "FINAL_OUTPUT_MANIFEST.json", out_sub_dir / "FINAL_OUTPUT_MANIFEST.json")
        copy_if_exists(sub_dir / "SYSTEM.md", out_sub_dir / "SYSTEM.md")
        copy_if_exists(sub_dir / "RUNBOOK.md", out_sub_dir / "RUNBOOK.md")
        copy_if_exists(sub_dir / "ARTIFACTS.md", out_sub_dir / "ARTIFACTS.md")
        copy_if_exists(sub_dir / "final_game" / "unity" / "UNITY_BUILD_INFO.json", out_sub_dir / "final_game" / "unity" / "UNITY_BUILD_INFO.json")
        copy_tree_if_exists(sub_dir / "final_game" / "web", out_sub_dir / "final_game" / "web")

        web_index_rel = f"submissions/{c}/final_game/web/index.html"
        web_index_path = out_round_dir / web_index_rel
        unity_info_rel = f"submissions/{c}/final_game/unity/UNITY_BUILD_INFO.json"
        unity_info_path = out_round_dir / unity_info_rel
        published_games[c] = {
            "web_exists": web_index_path.exists(),
            "web_rel": web_index_rel,
            "unity_info_exists": unity_info_path.exists(),
            "unity_info_rel": unity_info_rel,
        }

    winner = "unknown"
    top_score = None
    leaderboard_path = results_dir / "leaderboard.json"
    if leaderboard_path.exists():
        lb = read_json(leaderboard_path)
        eligible_winner = lb.get("eligible_winner")
        if isinstance(eligible_winner, str) and eligible_winner.strip():
            winner = eligible_winner.strip()
        elif eligible_winner is None and lb.get("output_gate_enforced"):
            winner = "none"
        entries = lb.get("entries", [])
        if entries:
            if winner in {"unknown", ""}:
                winner = str(entries[0].get("competitor", "unknown"))
            top_score = entries[0].get("final_score", entries[0].get("total_score_0_to_100"))

    return {
        "round_id": round_id,
        "created_at_utc": round_manifest.get("created_at_utc"),
        "winner": winner,
        "top_score": top_score,
        "copied_results": sorted(copied_results),
        "published_games": published_games,
    }


def write_index(site_root: Path, rows: list[dict]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    lines: list[str] = []
    lines.append("<!doctype html>")
    lines.append("<html lang='en'><head><meta charset='utf-8'/>")
    lines.append("<meta name='viewport' content='width=device-width, initial-scale=1'/>")
    lines.append("<title>Faceoff Hub</title>")
    lines.append(
        "<style>body{font-family:Menlo,Consolas,monospace;background:#0e1525;color:#eaf2ff;margin:0}main{max-width:1100px;margin:0 auto;padding:18px}a{color:#7ed7ff}table{width:100%;border-collapse:collapse}th,td{border:1px solid #274064;padding:8px;text-align:left}th{background:#14233f}.meta{color:#9cb0cf;font-size:12px}</style>"
    )
    lines.append("</head><body><main>")
    lines.append("<h1>Simulation Faceoff Hub</h1>")
    lines.append(f"<p class='meta'>Generated: {generated}</p>")
    lines.append("<table><thead><tr><th>Round</th><th>Winner</th><th>Top Score</th><th>Artifacts</th><th>Final Outputs</th></tr></thead><tbody>")
    if rows:
        for r in rows:
            rid = r["round_id"]
            copied = set(r.get("copied_results", []))
            links_list: list[str] = []
            if "leaderboard.md" in copied:
                links_list.append(f"<a href='rounds/{rid}/results/leaderboard.md'>leaderboard</a>")
            if "recognition_registry.md" in copied:
                links_list.append(f"<a href='rounds/{rid}/results/recognition_registry.md'>recognition</a>")
            if "codex_birdseye.html" in copied:
                links_list.append(f"<a href='rounds/{rid}/results/codex_birdseye.html'>codex view</a>")
            if "gemini_birdseye.html" in copied:
                links_list.append(f"<a href='rounds/{rid}/results/gemini_birdseye.html'>gemini view</a>")
            if "ollama_birdseye.html" in copied:
                links_list.append(f"<a href='rounds/{rid}/results/ollama_birdseye.html'>ollama view</a>")
            links = " | ".join(links_list) if links_list else "n/a"
            games = r.get("published_games", {})
            game_links: list[str] = []
            for competitor in ["codex", "gemini", "ollama"]:
                g = games.get(competitor, {})
                web_link = (
                    f"<a href='rounds/{rid}/{g.get('web_rel')}'>"
                    f"{competitor} web</a>"
                    if g.get("web_exists")
                    else f"{competitor} web: n/a"
                )
                unity_link = (
                    f"<a href='rounds/{rid}/{g.get('unity_info_rel')}'>"
                    f"{competitor} unity</a>"
                    if g.get("unity_info_exists")
                    else f"{competitor} unity: n/a"
                )
                game_links.append(f"{web_link} / {unity_link}")
            games_cell = "<br/>".join(game_links) if game_links else "n/a"
            lines.append(
                f"<tr><td>{rid}</td><td>{r['winner']}</td><td>{r['top_score']}</td><td>{links}</td><td>{games_cell}</td></tr>"
            )
    else:
        lines.append("<tr><td colspan='5'>No rounds found.</td></tr>")
    lines.append("</tbody></table>")
    lines.append("</main></body></html>")
    (site_root / "index.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    rounds_root = Path(args.rounds_root)
    site_root = Path(args.site_root)

    if site_root.exists():
        shutil.rmtree(site_root)
    site_root.mkdir(parents=True, exist_ok=True)
    (site_root / ".nojekyll").write_text("", encoding="utf-8")
    (site_root / "rounds").mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    if rounds_root.exists():
        for round_dir in sorted([p for p in rounds_root.iterdir() if p.is_dir()]):
            out_round = site_root / "rounds" / round_dir.name
            out_round.mkdir(parents=True, exist_ok=True)
            rows.append(build_round_pages(round_dir, out_round))

    rows.sort(key=lambda x: x.get("round_id", ""), reverse=True)
    write_index(site_root, rows)
    print(str(site_root / "index.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
