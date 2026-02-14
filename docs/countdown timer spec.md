# ETA Countdown Timer for Scanning Screen

## Context

During scans, users see a progress bar and percentage but no indication of how long remains. For large libraries (1000+ items), scans can take several minutes. A countdown timer gives users confidence the scan is progressing and helps them decide whether to wait or step away.

The challenge: per-item duration varies wildly — cache hits are near-instant (~0.01s), API calls take 0.5-2s, and rate-limited retries can take longer. A naive `elapsed / progress` calculation would swing wildly. We need smoothing.

## Approach: Exponential Moving Average (EMA)

Instead of linear extrapolation, track a smoothed per-item duration using EMA (alpha=0.15, ~13-sample half-life). This adapts to the current mix of cache hits vs API calls within ~15 items while smoothing out individual spikes.

**Phase-aware:** Movie scans have two phases ("Checking" per-movie, then "Analyzing" per-collection) with different item counts and durations. The calculator resets when the phase key or total changes, briefly showing "Calculating..." before the new phase stabilises.

**Flicker protection:** Display text only updates every 2 seconds, even though progress fires per-item. Graduated rounding avoids false precision (e.g., "~25s" not "~23s").

## Files to Create/Modify

### New: `src/complexionist/eta.py`

`ETACalculator` dataclass with:
- `update(phase, current, total)` — called each progress tick, updates EMA
- `remaining_seconds` property — returns `float | None` (None if < 5 samples)
- `format_remaining()` — returns display string like `"~2m 30s remaining"`, `"Calculating..."`, or `""`
- `reset()` — full reset for new scan
- Phase detection via `_extract_phase_key()` — splits `"Checking: Movie Name"` → `"Checking"`
- Phase reset triggers on: phase key change OR total change (handles "Both" scan where movie and TV both use "Analyzing")

Format examples: `~7s remaining`, `~25s remaining`, `~2m 30s remaining`, `~1h 15m remaining`

### Modify: `src/complexionist/gui/screens/scanning.py`

1. Add `self.eta_calculator = ETACalculator()` and `self.eta_text = ft.Text(...)` in `__init__`
2. In `update_progress()`, after the progress bar update inside `if total > 0:`:
   - Call `self.eta_calculator.update(phase, current, total)`
   - Set `self.eta_text.value = self.eta_calculator.format_remaining()`
   - Clear eta_text in the `else` (indeterminate) branch
3. Add `self.eta_text` to `build()` layout between the percentage and API stats lines
4. Clear eta_text in scan completion

Result layout:
```
[progress bar]
45 / 250
30% complete
~2m 30s remaining       ← NEW
Time: 12.3s | TMDB 45 | Cache hits: 60%
[Cancel]
```

### New: `tests/test_eta.py`

Tests for: no estimate before min_samples, estimate after enough samples, phase transition resets, total-change resets, indeterminate returns empty, format_seconds output, flicker protection, phase key extraction.

## Verification

1. `uv run pytest tests/test_eta.py -v` — unit tests pass
2. `uv run pytest tests/ -v` — full suite still passes
3. `uv run ruff check src tests && uv run ruff format --check src tests` — lint clean
4. Build exe and run a scan — verify countdown appears after ~5 items, updates smoothly, resets between phases, clears on completion
