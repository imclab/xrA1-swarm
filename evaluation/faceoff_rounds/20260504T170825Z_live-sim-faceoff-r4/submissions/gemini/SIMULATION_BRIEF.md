# Submission Brief: gemini

Round: `20260504T170825Z_live-sim-faceoff-r4`
Competitor: `gemini`
Time Limit: `10` minutes

## Mission
Build the most engaging and useful simulation + data visualization that can:
1. Replay its own build/execution approach.
2. Replay other agents/users' approaches.
3. Show live creation activity when available.
4. Show an interactive 3D view of how the code architecture works in real time.

## Required Platform Targets
- Web browser: macOS, Windows, mobile, visionOS browser, Quest browser.
- Unity standalone iOS app (viewer/player endpoint).

## Technology Freedom
- Any web/game engine technology is allowed.
- Preferred: Unity + WebGPU.
- 2D-to-3D evolution is allowed.
- Open source, custom shaders, VFX Graph, Gaussian splats, LiveKit, WebRTC,
  and other modern approaches are allowed.

## Mandatory Constraints
- Modular and cross-platform.
- Clear `what/when/where/why` visibility.
- Low compute/token/API overhead.
- Documented and extensible architecture.
- Full autonomy within legal, ethical, security, and financial guardrails.

## Outputs
- `SYSTEM.md`: architecture + module boundaries.
- `RUNBOOK.md`: build/test/run/deploy steps.
- `ARTIFACTS.md`: evidence of tests + measurements.
- `FINAL_OUTPUT_MANIFEST.json`: authoritative manifest for web + Unity launch targets.
- `final_game/web/index.html`: runnable web entrypoint (required for scoring).
- `final_game/unity/UNITY_BUILD_INFO.json`: Unity build/project descriptor (required for scoring).
- `SUBMISSION_METRICS.json`: manual/auto scores supplement.
- `INNOVATIONS.md`: unique ideas and differentiators.
- `SYSTEM_IMPROVEMENTS.md`: proposals to improve the core swarm system.
- `CREDITS.json`: human/agent contribution attribution.
- `CITATIONS.md`: cross-citations and collaboration references.
