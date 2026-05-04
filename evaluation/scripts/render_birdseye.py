#!/usr/bin/env python3
"""
Generate a bird's-eye animated HTML timeline for agent events.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render animated bird's-eye event timeline.")
    parser.add_argument("--run-dir", required=True, help="Path to run directory.")
    parser.add_argument(
        "--write-html",
        required=True,
        help="Output HTML path (typically in evaluation/reports).",
    )
    parser.add_argument(
        "--title",
        default="Agent Bird's-Eye View",
        help="Document title.",
    )
    parser.add_argument(
        "--round-minutes",
        type=int,
        default=10,
        help="Countdown duration in minutes (default: 10).",
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


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_html(title: str, manifest: dict, events: list[dict], round_minutes: int) -> str:
    events_sorted = sorted(events, key=lambda r: (int(r.get("start_ms", 0)), str(r.get("agent_id", ""))))
    lane_map: dict[str, str] = {}
    for event in events_sorted:
        lane_map.setdefault(str(event.get("agent_id", "unknown")), str(event.get("agent_role", "unknown")))

    lanes = [{"agent_id": k, "agent_role": v} for k, v in lane_map.items()]
    max_end = 1
    for event in events_sorted:
        end_ms = int(event.get("start_ms", 0)) + int(event.get("duration_ms", 0))
        if end_ms > max_end:
            max_end = end_ms

    data_blob = {
        "title": title,
        "run_id": manifest.get("run_id", "unknown"),
        "provider": manifest.get("provider", "unknown"),
        "model": manifest.get("model", "unknown"),
        "round_minutes": round_minutes,
        "lanes": lanes,
        "events": events_sorted,
        "duration_ms": max_end,
    }

    data_json = json.dumps(data_blob)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html_escape(title)}</title>
  <style>
    :root {{
      --bg: #0b1220;
      --panel: #111b2f;
      --text: #eaf2ff;
      --muted: #98a7c4;
      --line: #223252;
      --ok: #28c76f;
      --warn: #ffb020;
      --bad: #ff5c7c;
      --run: #40c4ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      background: radial-gradient(circle at 20% 0%, #15243f, var(--bg) 42%);
      color: var(--text);
    }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 18px; }}
    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 12px;
    }}
    .meta {{ color: var(--muted); font-size: 12px; }}
    .countdown {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid #2a3f68;
      background: linear-gradient(180deg, rgba(64,196,255,0.10), rgba(255,176,32,0.06));
      border-radius: 14px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }}
    .countdown-clock {{
      font-size: 26px;
      font-weight: 700;
      letter-spacing: 1px;
      color: #ffffff;
    }}
    .countdown-label {{
      font-size: 11px;
      color: var(--muted);
    }}
    .countdown.urgent {{
      border-color: rgba(255,92,124,0.8);
      box-shadow: 0 0 24px rgba(255,92,124,0.26);
      animation: pulse 0.9s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0% {{ transform: scale(1); }}
      50% {{ transform: scale(1.01); }}
      100% {{ transform: scale(1); }}
    }}
    .btn {{
      appearance: none;
      border: 1px solid #2f4f80;
      background: #193158;
      color: #eaf2ff;
      border-radius: 10px;
      padding: 7px 11px;
      font-size: 11px;
      cursor: pointer;
    }}
    .btn[disabled] {{
      opacity: 0.6;
      cursor: default;
    }}
    .timeline {{
      position: relative;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--panel);
      padding: 12px;
      min-height: 260px;
    }}
    .lane {{
      position: relative;
      height: 44px;
      border-bottom: 1px dashed #1d2a45;
      margin-bottom: 8px;
      padding-left: 170px;
    }}
    .lane:last-child {{ border-bottom: 0; }}
    .lane-label {{
      position: absolute;
      left: 0;
      top: 12px;
      width: 164px;
      color: var(--muted);
      font-size: 11px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .event {{
      position: absolute;
      top: 10px;
      height: 22px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.2);
      background: #2d4874;
      color: #f5fbff;
      font-size: 10px;
      padding: 3px 6px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }}
    .event.completed {{ background: rgba(40,199,111,0.35); }}
    .event.running, .event.started {{ background: rgba(64,196,255,0.35); }}
    .event.blocked, .event.failed {{ background: rgba(255,92,124,0.35); }}
    .event.skipped {{ background: rgba(255,176,32,0.35); }}
    .playhead {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 2px;
      background: var(--run);
      box-shadow: 0 0 12px var(--run);
      pointer-events: none;
      animation: scan linear infinite;
    }}
    @keyframes scan {{
      from {{ left: 170px; }}
      to {{ left: calc(170px + var(--timeline-width)); }}
    }}
    .legend {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; font-size: 11px; color: var(--muted); }}
    .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }}
    .list {{ margin-top: 10px; font-size: 11px; color: var(--muted); max-height: 220px; overflow: auto; }}
    .list-row {{ padding: 6px 8px; border-bottom: 1px solid #1d2a45; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div><strong>{html_escape(title)}</strong></div>
      <div class="meta">Run: <span id="run-id"></span> | Provider: <span id="provider"></span> | Model: <span id="model"></span></div>
    </div>
    <div class="countdown" id="countdown">
      <div>
        <div class="countdown-clock" id="countdown-clock">10:00</div>
        <div class="countdown-label" id="countdown-label">Ship before the buzzer.</div>
      </div>
      <button class="btn" id="sound-btn">Enable Sound</button>
    </div>
    <div class="card timeline" id="timeline"></div>
    <div class="card">
      <div class="legend">
        <span><i class="dot" style="background: rgba(64,196,255,0.8)"></i>started/running</span>
        <span><i class="dot" style="background: rgba(40,199,111,0.8)"></i>completed</span>
        <span><i class="dot" style="background: rgba(255,92,124,0.8)"></i>failed/blocked</span>
        <span><i class="dot" style="background: rgba(255,176,32,0.8)"></i>skipped</span>
      </div>
      <div class="list" id="event-list"></div>
    </div>
  </div>
  <script>
    const data = {data_json};
    const pxPerMs = 0.0035;
    const timeline = document.getElementById("timeline");
    const eventList = document.getElementById("event-list");
    const countdown = document.getElementById("countdown");
    const countdownClock = document.getElementById("countdown-clock");
    const countdownLabel = document.getElementById("countdown-label");
    const soundBtn = document.getElementById("sound-btn");
    document.getElementById("run-id").textContent = data.run_id;
    document.getElementById("provider").textContent = data.provider;
    document.getElementById("model").textContent = data.model;

    const width = Math.max(860, Math.ceil(data.duration_ms * pxPerMs));
    timeline.style.setProperty("--timeline-width", `${{width}}px`);
    timeline.style.setProperty("animation-duration", `${{Math.max(6, data.duration_ms / 800)}}s`);

    for (const lane of data.lanes) {{
      const laneEl = document.createElement("div");
      laneEl.className = "lane";
      laneEl.style.width = `${{170 + width}}px`;

      const label = document.createElement("div");
      label.className = "lane-label";
      label.textContent = `${{lane.agent_id}} (${{lane.agent_role}})`;
      laneEl.appendChild(label);

      const laneEvents = data.events.filter(e => e.agent_id === lane.agent_id);
      for (const e of laneEvents) {{
        const bar = document.createElement("div");
        bar.className = `event ${{e.status}}`;
        bar.style.left = `${{170 + Math.floor(e.start_ms * pxPerMs)}}px`;
        bar.style.width = `${{Math.max(36, Math.floor(e.duration_ms * pxPerMs))}}px`;
        bar.title = `Scenario ${{e.scenario_id}} | what=${{e.what}} | where=${{e.where}} | why=${{e.why}}`;
        bar.textContent = `${{e.scenario_id}} ${{e.what}}`;
        laneEl.appendChild(bar);
      }}

      timeline.appendChild(laneEl);
    }}

    const playhead = document.createElement("div");
    playhead.className = "playhead";
    playhead.style.animationDuration = `${{Math.max(6, data.duration_ms / 800)}}s`;
    timeline.appendChild(playhead);

    for (const e of data.events) {{
      const row = document.createElement("div");
      row.className = "list-row";
      row.textContent = `${{e.scenario_id}} | ${{e.agent_id}} | ${{e.status}} | what=${{e.what}} | where=${{e.where}} | why=${{e.why}}`;
      eventList.appendChild(row);
    }}

    const roundMs = Math.max(1, Number(data.round_minutes || 10)) * 60 * 1000;
    const halfMs = Math.floor(roundMs / 2);
    const finalThreeMs = 3 * 60 * 1000;
    const cueState = {{
      start: false,
      half: false,
      finalThree: false,
      buzzer: false,
      lastFinalPulseSec: -1
    }};

    let audioCtx = null;
    let soundEnabled = false;
    function ensureAudio() {{
      if (!audioCtx) {{
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return false;
        audioCtx = new Ctx();
      }}
      return true;
    }}
    function beep(freq, durationMs, gainVal = 0.06) {{
      if (!soundEnabled || !audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      gain.gain.value = gainVal;
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      setTimeout(() => osc.stop(), durationMs);
    }}
    function cueStart() {{
      beep(780, 140); setTimeout(() => beep(920, 160), 180);
    }}
    function cueHalf() {{
      beep(640, 180); setTimeout(() => beep(640, 180), 240);
    }}
    function cueFinalThree() {{
      beep(950, 200); setTimeout(() => beep(860, 220), 260); setTimeout(() => beep(950, 260), 560);
    }}
    function cueBuzzer() {{
      beep(420, 600, 0.08); setTimeout(() => beep(360, 700, 0.08), 640);
    }}

    soundBtn.addEventListener("click", () => {{
      if (ensureAudio()) {{
        soundEnabled = true;
        soundBtn.textContent = "Sound On";
        soundBtn.disabled = true;
        cueStart();
      }} else {{
        soundBtn.textContent = "No Audio API";
        soundBtn.disabled = true;
      }}
    }});

    const startTs = Date.now();
    function fmt(ms) {{
      const totalSec = Math.max(0, Math.floor(ms / 1000));
      const mm = Math.floor(totalSec / 60);
      const ss = totalSec % 60;
      return `${{String(mm).padStart(2, "0")}}:${{String(ss).padStart(2, "0")}}`;
    }}

    function tickCountdown() {{
      const elapsed = Date.now() - startTs;
      const remaining = Math.max(0, roundMs - elapsed);
      countdownClock.textContent = fmt(remaining);

      if (!cueState.start) {{
        cueState.start = true;
        if (soundEnabled) cueStart();
      }}

      if (!cueState.half && remaining <= halfMs) {{
        cueState.half = true;
        countdownLabel.textContent = "Halfway. Focus and ship.";
        if (soundEnabled) cueHalf();
      }}

      if (!cueState.finalThree && remaining <= finalThreeMs) {{
        cueState.finalThree = true;
        countdown.classList.add("urgent");
        countdownLabel.textContent = "Final 3 minutes. Wrap up now.";
        if (soundEnabled) cueFinalThree();
      }}

      if (remaining <= finalThreeMs && remaining > 0) {{
        const secLeft = Math.floor(remaining / 1000);
        if (secLeft % 30 === 0 && secLeft !== cueState.lastFinalPulseSec) {{
          cueState.lastFinalPulseSec = secLeft;
          if (soundEnabled) beep(1100, 90, 0.05);
        }}
      }}

      if (!cueState.buzzer && remaining <= 0) {{
        cueState.buzzer = true;
        countdown.classList.add("urgent");
        countdownLabel.textContent = "Buzzer. Submit what you have.";
        if (soundEnabled) cueBuzzer();
      }}
      requestAnimationFrame(tickCountdown);
    }}
    requestAnimationFrame(tickCountdown);
  </script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    manifest_path = run_dir / "run_manifest.json"
    events_path = run_dir / "agent_events.jsonl"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    if not events_path.exists():
        raise FileNotFoundError(f"Missing events: {events_path}")

    manifest = read_json(manifest_path)
    events = read_jsonl(events_path)
    html = build_html(args.title, manifest, events, args.round_minutes)

    out_path = Path(args.write_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
