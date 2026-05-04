#!/usr/bin/env python3
"""
Compile a faceoff leaderboard from competitor run directories.

Scoring policy:
- Primary basis: shipped final outputs (game/simulation/visualization deliverables).
- Supporting basis: run telemetry + timeline observability metrics.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

VALID_FINAL_STATUS = {"ready", "complete", "submitted"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile faceoff leaderboard.")
    parser.add_argument("--round-dir", required=True, help="Round directory created by bootstrap script.")
    parser.add_argument("--codex-run-dir", default=None, help="Run directory for codex.")
    parser.add_argument("--gemini-run-dir", default=None, help="Run directory for gemini.")
    parser.add_argument("--ollama-run-dir", default=None, help="Run directory for ollama.")
    parser.add_argument(
        "--no-output-gate",
        action="store_true",
        help="Allow non-zero scores even when required final outputs are missing.",
    )
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


def scale_0_5(values: list[float]) -> list[float]:
    return [max(0.0, min(1.0, float(v) / 5.0)) for v in values]


def scale_pct(values: list[float]) -> list[float]:
    return [max(0.0, min(1.0, float(v) / 100.0)) for v in values]


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


def resolve_output_path(base: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    p = Path(raw)
    if p.is_absolute():
        return p
    return base / p


def looks_placeholder_markdown(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return True
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return True
    if "- [ ]" in text:
        return True
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) <= 2:
        return True
    return False


def evaluate_final_outputs(round_dir: Path, competitor: str, requirements: dict) -> dict:
    sub_dir = round_dir / "submissions" / competitor
    output_manifest_path = sub_dir / "FINAL_OUTPUT_MANIFEST.json"
    output_manifest = read_json(output_manifest_path) if output_manifest_path.exists() else {}

    req_docs = requirements.get("required_docs", ["SYSTEM.md", "RUNBOOK.md", "ARTIFACTS.md"])
    web_req = requirements.get("web", {}) or {}
    unity_req = requirements.get("unity", {}) or {}

    web_entry_rel = output_manifest.get("web_entrypoint") or web_req.get("required_entrypoint") or "final_game/web/index.html"
    unity_info_rel = output_manifest.get("unity_build_info") or unity_req.get("required_build_info") or "final_game/unity/UNITY_BUILD_INFO.json"

    web_entry_path = resolve_output_path(sub_dir, str(web_entry_rel))
    unity_info_path = resolve_output_path(sub_dir, str(unity_info_rel))

    web_ok = bool(web_entry_path and web_entry_path.exists() and web_entry_path.is_file() and web_entry_path.stat().st_size > 0)
    unity_info = read_json(unity_info_path) if unity_info_path and unity_info_path.exists() else {}
    unity_info_ok = bool(unity_info_path and unity_info_path.exists() and unity_info_path.stat().st_size > 0)

    unity_project_raw = str(output_manifest.get("unity_project_path") or unity_info.get("project_path") or "").strip()
    unity_build_raw = str(output_manifest.get("unity_build_path") or unity_info.get("build_path") or "").strip()

    unity_project_path = resolve_output_path(sub_dir, unity_project_raw) if unity_project_raw else None
    unity_build_path = resolve_output_path(sub_dir, unity_build_raw) if unity_build_raw else None
    unity_project_ok = bool(unity_project_path and unity_project_path.exists())
    unity_build_ok = bool(unity_build_path and unity_build_path.exists())
    unity_ok = unity_info_ok and (unity_project_ok or unity_build_ok)
    manifest_status = str(output_manifest.get("status", "")).strip().lower()
    unity_status = str(unity_info.get("status", "")).strip().lower()

    doc_state: dict[str, bool] = {}
    for doc in req_docs:
        p = sub_dir / doc
        doc_state[doc] = p.exists() and p.is_file() and p.stat().st_size > 0 and not looks_placeholder_markdown(p)
    docs_ok = all(doc_state.values()) if doc_state else False

    missing: list[str] = []
    if not web_ok:
        missing.append(f"missing_web_entrypoint:{web_entry_rel}")
    if not unity_info_ok:
        missing.append(f"missing_unity_build_info:{unity_info_rel}")
    if unity_info_ok and not unity_ok:
        missing.append("missing_unity_project_or_build_path")
    if manifest_status not in VALID_FINAL_STATUS:
        missing.append("manifest_status_not_final")
    if unity_status and unity_status not in VALID_FINAL_STATUS:
        missing.append("unity_status_not_final")
    for d, ok in doc_state.items():
        if not ok:
            missing.append(f"missing_doc:{d}")

    game_output_score = 0.0
    if web_ok:
        game_output_score += 2.0
    if unity_ok:
        game_output_score += 2.0
    if docs_ok:
        game_output_score += 1.0

    gate_pass = web_ok and unity_ok and docs_ok and manifest_status in VALID_FINAL_STATUS and (not unity_status or unity_status in VALID_FINAL_STATUS)
    return {
        "output_manifest_path": str(output_manifest_path),
        "output_manifest_exists": output_manifest_path.exists(),
        "web_entrypoint": str(web_entry_rel),
        "web_entrypoint_exists": web_ok,
        "unity_build_info": str(unity_info_rel),
        "unity_build_info_exists": unity_info_ok,
        "unity_project_path": str(unity_project_raw),
        "unity_project_exists": unity_project_ok,
        "unity_build_path": str(unity_build_raw),
        "unity_build_exists": unity_build_ok,
        "required_docs": req_docs,
        "doc_status": doc_state,
        "docs_complete": docs_ok,
        "manifest_status": manifest_status,
        "unity_status": unity_status,
        "game_output_score_0_to_5": game_output_score,
        "output_gate_pass": gate_pass,
        "missing_output_requirements": missing,
    }


def main() -> int:
    args = parse_args()
    round_dir = Path(args.round_dir)
    manifest = read_json(round_dir / "round_manifest.json")
    requirements = manifest.get("final_output_requirements", {})

    run_paths: list[Path] = []
    for maybe in [args.codex_run_dir, args.gemini_run_dir, args.ollama_run_dir]:
        if maybe:
            run_paths.append(Path(maybe))

    entries: list[dict] = []
    for run_dir in run_paths:
        metrics = collect_metrics(run_dir)
        competitor = competitor_name(metrics["provider"])
        manual = load_manual_scores(round_dir, competitor)
        credits = load_credits(round_dir, competitor)
        output_eval = evaluate_final_outputs(round_dir, competitor, requirements)
        improvements_count = count_markdown_bullets(round_dir / "submissions" / competitor / "SYSTEM_IMPROVEMENTS.md")
        innovations_count = count_markdown_bullets(round_dir / "submissions" / competitor / "INNOVATIONS.md")
        breakthroughs_count = count_markdown_bullets(round_dir / "submissions" / competitor / "BREAKTHROUGHS.md")

        metrics["competitor"] = competitor
        metrics["improvement_proposals_count"] = improvements_count
        metrics["innovation_items_count"] = innovations_count
        metrics["breakthrough_items_count"] = breakthroughs_count
        metrics["human_contributor_count"] = len(credits.get("human_contributors", []) or [])
        metrics["agent_contributor_count"] = len(credits.get("agent_contributors", []) or [])
        metrics.update(output_eval)
        metrics["manual"] = {
            "engagement_score_0_to_5": clamp_0_5(manual.get("engagement_score_0_to_5")),
            "usefulness_score_0_to_5": clamp_0_5(manual.get("usefulness_score_0_to_5")),
            "observability_clarity_0_to_5": clamp_0_5(manual.get("observability_clarity_0_to_5")),
            "novelty_score_0_to_5": clamp_0_5(manual.get("novelty_score_0_to_5")),
            "interactive_3d_clarity_0_to_5": clamp_0_5(manual.get("interactive_3d_clarity_0_to_5")),
            "architecture_visibility_0_to_5": clamp_0_5(manual.get("architecture_visibility_0_to_5")),
            "realtime_process_trace_0_to_5": clamp_0_5(manual.get("realtime_process_trace_0_to_5")),
            "webgpu_unity_parity_0_to_5": clamp_0_5(manual.get("webgpu_unity_parity_0_to_5")),
            "performance_efficiency_0_to_5": clamp_0_5(manual.get("performance_efficiency_0_to_5")),
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

    output_vals = [e["game_output_score_0_to_5"] for e in entries]
    success_vals = [e["success_rate_pct"] for e in entries]
    token_vals = [e["avg_tokens_per_task"] for e in entries]
    visualization_vals = [
        (
            e["manual"]["interactive_3d_clarity_0_to_5"]
            + e["manual"]["realtime_process_trace_0_to_5"]
        ) / 2.0
        for e in entries
    ]
    architecture_vals = [e["manual"]["architecture_visibility_0_to_5"] for e in entries]
    parity_vals = [e["manual"]["webgpu_unity_parity_0_to_5"] for e in entries]

    output_n = scale_0_5(output_vals)
    success_n = scale_pct(success_vals)
    token_n = normalize(token_vals, higher_is_better=False)
    visualization_n = scale_0_5(visualization_vals)
    architecture_n = scale_0_5(architecture_vals)
    parity_n = scale_0_5(parity_vals)

    weights = manifest.get("scoring_weights", {})
    w_output = float(weights.get("game_output_completeness", 0.55))
    w_viz = float(weights.get("interactive_3d_visualization", 0.20))
    w_arch = float(weights.get("architecture_visibility_realtime", 0.20))
    w_parity = float(weights.get("webgpu_unity_parity", 0.10))
    w_token = float(weights.get("efficiency_tokens_inverse", 0.03))
    w_success = float(weights.get("reliability_success_rate", 0.02))

    bonus_max = float(manifest.get("bonus_policy", {}).get("open_standards_and_open_source_max_points", 10))
    breakthrough_bonus_max = float(manifest.get("bonus_policy", {}).get("breakthrough_discovery_max_points", 10))

    scored: list[dict] = []
    for i, entry in enumerate(entries):
        base_score = (
            w_output * output_n[i]
            + w_viz * visualization_n[i]
            + w_arch * architecture_n[i]
            + w_parity * parity_n[i]
            + w_success * success_n[i]
            + w_token * token_n[i]
        )
        m = entry["manual"]
        bonus_ratio = (m["open_standards_score_0_to_5"] + m["open_source_contribution_score_0_to_5"]) / 10.0
        bonus_score = bonus_ratio * bonus_max
        breakthrough_bonus = (m["breakthrough_score_0_to_5"] / 5.0) * breakthrough_bonus_max
        citation_bonus = min(5.0, float(m["citation_count"]) * 0.5)
        collaboration_bonus = min(5.0, float(m["collaboration_link_count"]) * 0.5)
        peer_bonus = min(5.0, float(m["peer_votes"]) * 0.2)
        merit_bonus = citation_bonus + collaboration_bonus + peer_bonus

        raw_base_0_to_100 = round(base_score * 100.0, 2)
        raw_final = round(raw_base_0_to_100 + bonus_score + breakthrough_bonus + merit_bonus, 2)
        gated_final = raw_final
        if not args.no_output_gate and not entry["output_gate_pass"]:
            gated_final = 0.0

        entry["total_score_0_to_100"] = raw_base_0_to_100
        entry["bonus_score"] = round(bonus_score, 2)
        entry["breakthrough_bonus_score"] = round(breakthrough_bonus, 2)
        entry["merit_bonus_score"] = round(merit_bonus, 2)
        entry["raw_final_score"] = raw_final
        entry["final_score"] = round(gated_final, 2)
        scored.append(entry)

    scored.sort(
        key=lambda e: (
            e["final_score"],
            e["game_output_score_0_to_5"],
            e["success_rate_pct"],
        ),
        reverse=True,
    )
    for rank, entry in enumerate(scored, start=1):
        entry["rank"] = rank

    eligible = [e for e in scored if e.get("output_gate_pass")]
    winner = eligible[0] if eligible else None

    results_dir = round_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    leaderboard_json = {
        "round_id": manifest.get("round_id"),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scoring_basis": "final_game_outputs_primary",
        "output_gate_enforced": not args.no_output_gate,
        "eligible_winner": winner.get("competitor") if winner else None,
        "entries": scored,
    }
    (results_dir / "leaderboard.json").write_text(json.dumps(leaderboard_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# Leaderboard")
    lines.append("")
    lines.append(f"Round: `{manifest.get('round_id')}`")
    lines.append("")
    lines.append("Scoring basis: **final games/simulations/data visualizations** (web + Unity outputs).")
    lines.append("")
    lines.append(
        "| Rank | Competitor | Final | Raw Final | Base | Output 0-5 | 3D Viz | Arch/RT | Parity | Gate | Web | Unity | Docs | Success % | Avg Tokens | Run Dir |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|---|")
    for e in scored:
        m = e["manual"]
        viz = (m["interactive_3d_clarity_0_to_5"] + m["realtime_process_trace_0_to_5"]) / 2.0
        arch = m["architecture_visibility_0_to_5"]
        parity = m["webgpu_unity_parity_0_to_5"]
        gate = "pass" if e["output_gate_pass"] else "fail"
        web = "yes" if e["web_entrypoint_exists"] else "no"
        unity = "yes" if (e["unity_build_info_exists"] and (e["unity_project_exists"] or e["unity_build_exists"])) else "no"
        docs = "yes" if e["docs_complete"] else "no"
        lines.append(
            f"| {e['rank']} | {e['competitor']} | {e['final_score']:.2f} | {e['raw_final_score']:.2f} | "
            f"{e['total_score_0_to_100']:.2f} | {e['game_output_score_0_to_5']:.2f} | {viz:.2f} | {arch:.2f} | {parity:.2f} | "
            f"{gate} | {web} | {unity} | {docs} | {e['success_rate_pct']:.2f} | {e['avg_tokens_per_task']:.0f} | `{e['run_dir']}` |"
        )

    lines.append("")
    if winner:
        lines.append(
            f"Winner: `{winner['competitor']}` with final score `{winner['final_score']:.2f}` "
            f"(output gate passed and complete final deliverables present)."
        )
    else:
        lines.append("Winner: `none` (no competitor passed required final output gate for web + Unity + docs).")
    lines.append("")
    lines.append("Missing requirements per competitor:")
    for e in scored:
        missing = e.get("missing_output_requirements", [])
        if not missing:
            lines.append(f"- `{e['competitor']}`: none")
        else:
            lines.append(f"- `{e['competitor']}`: {', '.join(missing)}")

    (results_dir / "leaderboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(results_dir / "leaderboard.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
