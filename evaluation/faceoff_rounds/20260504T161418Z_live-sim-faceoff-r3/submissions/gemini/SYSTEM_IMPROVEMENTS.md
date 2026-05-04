# System Improvements

- Add strict model-tier router to enforce economy-vs-advanced model selection per task class.
- Add automatic per-round metric snapshots (tokens/speed/quality) into a single JSON timeseries.
- Add regression alerts when speed or quality drifts across consecutive rounds.
- Add provider adapter parity tests so cross-CLI behavior remains consistent.
