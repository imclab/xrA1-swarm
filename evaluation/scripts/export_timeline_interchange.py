#!/usr/bin/env python3
"""
Export run timeline into sparse multi-viewer interchange formats.

Outputs:
- timeline.canonical.json
- timeline.xrai.json
- timeline.events.jsonl
- timeline.rerun.ndjson
- timeline.index.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a run as cross-viewer timeline interchange bundle.")
    parser.add_argument("--run-dir", required=True, help="Run directory path.")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Default: <run-dir>/playback_bundle",
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


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")


def build_entities(events: list[dict]) -> list[dict]:
    seen = {}
    for e in events:
        aid = str(e.get("agent_id", "unknown"))
        if aid not in seen:
            seen[aid] = {
                "id": aid,
                "kind": "agent",
                "label": aid,
                "attrs": {
                    "agent_role": e.get("agent_role"),
                },
            }
    return list(seen.values())


def to_canonical(manifest: dict, events: list[dict]) -> dict:
    ordered = sorted(events, key=lambda x: (int(x.get("start_ms", 0)), str(x.get("agent_id", ""))))
    entities = build_entities(ordered)
    canonical_events = []
    for idx, e in enumerate(ordered, start=1):
        t0 = int(e.get("start_ms", 0))
        dur = int(e.get("duration_ms", 0))
        t1 = t0 + dur
        canonical_events.append(
            {
                "id": f"ev_{idx:05d}",
                "t0_ms": t0,
                "t1_ms": t1,
                "entity_id": str(e.get("agent_id", "unknown")),
                "scenario_id": str(e.get("scenario_id", "")),
                "phase": str(e.get("agent_role", "")) if e.get("agent_role") is not None else None,
                "what": str(e.get("what", "")),
                "where": str(e.get("where", "")),
                "why": str(e.get("why", "")),
                "status": str(e.get("status", "")),
                "metrics": {
                    "duration_ms": dur,
                    "tokens_total": int(e.get("tokens_total", 0)),
                },
            }
        )

    return {
        "spec_version": "xrai-timeline-0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run": {
            "run_id": manifest.get("run_id"),
            "provider": manifest.get("provider"),
            "model": manifest.get("model"),
            "branch": manifest.get("branch"),
            "commit": manifest.get("commit"),
        },
        "time": {
            "unit": "ms",
            "origin": "run_start",
        },
        "entities": entities,
        "events": canonical_events,
    }


def to_xrai(canonical: dict) -> dict:
    return {
        "xrai": {
            "version": "0.1",
            "kind": "timeline_interchange",
            "source": {
                "run_id": canonical.get("run", {}).get("run_id"),
                "provider": canonical.get("run", {}).get("provider"),
                "model": canonical.get("run", {}).get("model"),
            },
            "timeline": canonical.get("events", []),
            "entities": canonical.get("entities", []),
            "meta": {
                "created_at_utc": canonical.get("created_at_utc"),
                "time_unit": "ms",
                "origin": "run_start",
            },
        }
    }


def to_rerun_ndjson(canonical: dict) -> list[dict]:
    rows: list[dict] = []
    for ev in canonical.get("events", []):
        path = f"/agents/{ev.get('entity_id')}/scenarios/{ev.get('scenario_id')}"
        rows.append(
            {
                "time_ms": ev.get("t0_ms"),
                "path": path,
                "kind": "interval_start",
                "components": {
                    "xrai.what": ev.get("what"),
                    "xrai.where": ev.get("where"),
                    "xrai.why": ev.get("why"),
                    "xrai.status": ev.get("status"),
                    "xrai.phase": ev.get("phase"),
                },
            }
        )
        rows.append(
            {
                "time_ms": ev.get("t1_ms"),
                "path": path,
                "kind": "interval_end",
                "components": {
                    "xrai.duration_ms": ev.get("metrics", {}).get("duration_ms"),
                    "xrai.tokens_total": ev.get("metrics", {}).get("tokens_total"),
                },
            }
        )
    return rows


def build_index(bundle_dir: Path, canonical: dict) -> dict:
    return {
        "bundle_version": "timeline-bundle-0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": canonical.get("run", {}).get("run_id"),
        "artifacts": {
            "canonical_json": str(bundle_dir / "timeline.canonical.json"),
            "xrai_json": str(bundle_dir / "timeline.xrai.json"),
            "events_jsonl": str(bundle_dir / "timeline.events.jsonl"),
            "rerun_ndjson": str(bundle_dir / "timeline.rerun.ndjson")
        },
        "viewer_adapters": {
            "rerun_io": "Use timeline.rerun.ndjson as source stream for logging adapters.",
            "unity_unreal_webgl_webxr": "Use timeline.canonical.json or timeline.xrai.json.",
            "d3_plotly_canvas_cesium": "Use timeline.events.jsonl for direct charting.",
            "portals_app": "Prefer timeline.xrai.json for metadata-rich playback."
        }
    }


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    manifest_path = run_dir / "run_manifest.json"
    events_path = run_dir / "agent_events.jsonl"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    if not events_path.exists():
        raise FileNotFoundError(f"Missing events: {events_path}")

    out_dir = Path(args.out_dir) if args.out_dir else (run_dir / "playback_bundle")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_json(manifest_path)
    events = read_jsonl(events_path)
    canonical = to_canonical(manifest, events)
    xrai = to_xrai(canonical)
    rerun_rows = to_rerun_ndjson(canonical)

    write_json(out_dir / "timeline.canonical.json", canonical)
    write_json(out_dir / "timeline.xrai.json", xrai)
    write_jsonl(out_dir / "timeline.events.jsonl", canonical.get("events", []))
    write_jsonl(out_dir / "timeline.rerun.ndjson", rerun_rows)
    write_json(out_dir / "timeline.index.json", build_index(out_dir, canonical))

    print(str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
