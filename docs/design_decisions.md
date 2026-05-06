# Design Decisions

## 1. `get_test_info()` as a single source of truth

All test parameters (port, command, sample count, interval, deadline) are assembled once in `get_test_info()` and consumed by both `run_test()` and `run_all_tests.py`. This avoids duplicating config-parsing logic across callers and means the YAML structure only needs to be understood in one place.

## 2. Deadline + count as dual stop conditions

The sampling loop stops when either `measurements_count` is reached **or** `total_duration_seconds` expires. This makes the two config values independently meaningful: count caps the data volume, duration caps the wall-clock time. If the values are consistent (10 samples × 1 s = 10 s) the deadline never fires; if they diverge the test still terminates gracefully.

## 3. `ResultManager` uses human-readable filenames

Each result is saved as `results/data/<timestamp>_<ammeter_type>.json` (e.g. `20260506_142301_greenlee.json`). This gives:
- files that are sortable chronologically and immediately descriptive
- easy retrieval by name (`load("20260506_142301_greenlee")`)
- easy listing and comparison across runs (`list_results()`, `filter_by()`, `compare()`)

The UUID is still stored *inside* the JSON for a unique internal identifier, but kept out of the filename to keep it readable. No database is needed; plain JSON files are human-readable and portable.

## 4. `_compute_stats()` guards against empty measurements

If every sample fails, `statistics.mean([])` raises an exception. The private helper returns a zero-filled dict instead, so the result object is always well-formed and can be saved without crashing.

## 5. `compare_accuracy()` uses coefficient of variation (CV)

CV = std_dev / mean normalises spread relative to scale, making it fair to compare across ammeter types that produce measurements in very different ranges (ENTES produces values in the tens–hundreds of amps, CIRCUTOR in the milliamp range). Lower CV means more consistent readings.

## 6. `AmmeterPlotter` uses the `Agg` matplotlib backend

`matplotlib.use('Agg')` is set before any plot import. This prevents matplotlib from trying to open a display window, which would crash on headless servers or in CI. Plots are always saved as PNGs; passing `show=True` to the constructor re-enables interactive display for local use.

## 7. Logger guards against duplicate handlers

`logging.getLogger(name)` returns the same instance on repeated calls. Without the `if not logger.handlers` check, every new `TestLogger` instance would add another handler to the same underlying logger, producing duplicate log lines. The guard makes the setup idempotent.

## 8. Error simulation is config-driven and non-invasive

Error simulation is controlled entirely by `config/config.yaml` (`error_simulation.enabled`). When disabled it adds zero overhead — `_simulate_errors()` returns immediately. When enabled it injects three realistic failure modes:
- **drop** — measurement returns `None` (connection hiccup)
- **outlier** — value multiplied by `outlier_factor` (sensor spike)
- **exception** — raises `ConnectionError` (device offline)

All three map to the existing error handling in `run_test()`, so no special-case code was needed. Simulated errors are labelled in `result['errors']` so they're distinguishable from real failures in the saved JSON.


