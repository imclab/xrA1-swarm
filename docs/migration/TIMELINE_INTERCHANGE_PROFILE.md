# Timeline Interchange Profile

Version: `0.1`  
Date: `2026-05-04`

## Goal

Encode simulation construction/playback timelines in a sparse, portable format
that can be replayed in multiple viewers and engines.

## Canonical Model

Primary schema:
- [xrai_timeline.schema.json](/Users/jamestunick/Applications/xrA1-swarm-codemini/evaluation/schemas/xrai_timeline.schema.json)

Core fields:
- `who`: `entity_id` (agent/user/system)
- `what`: action summary
- `when`: `t0_ms`, `t1_ms`
- `where`: target path/module/system
- `why`: intent/rationale
- `status`: completed/failed/blocked/etc.

## Exported Bundle (per run)

`<run_dir>/playback_bundle/`
- `timeline.canonical.json`
- `timeline.xrai.json`
- `timeline.events.jsonl`
- `timeline.rerun.ndjson`
- `timeline.index.json`

## Viewer/Engine Mapping

- Rerun.io: consume `timeline.rerun.ndjson` via logging adapter.
- Unity/Unreal/WebGL/WebXR: consume `timeline.canonical.json` or `timeline.xrai.json`.
- Cesium/Canvas/D3/Plotly/Rust viewers: consume `timeline.events.jsonl`.
- Portals app/web viewers: consume `timeline.xrai.json`.

## Modes

- Flat 2D: charts + lanes from `events.jsonl`.
- Immersive VR: entity lanes as spatial paths or timelines.
- AR: overlay live/historical event markers in context.

## Generation Command

```bash
python3 evaluation/scripts/export_timeline_interchange.py \
  --run-dir evaluation/runs/<run_id>
```

## Design Principles

- Sparse by default, detail by optional extension fields.
- Format-neutral and adapter-first.
- Preserve strict attribution and merit visibility metadata.
