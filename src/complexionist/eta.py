"""ETA countdown calculator for scan progress.

Uses Exponential Moving Average (EMA) to smooth per-item duration estimates,
adapting to the current mix of cache hits vs API calls while filtering out
individual spikes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


def _extract_phase_key(phase: str) -> str:
    """Extract the phase action from a progress string.

    Splits "Checking: Movie Name" → "Checking".
    Returns the full string if no colon separator is found.
    """
    if ": " in phase:
        return phase.split(": ", 1)[0]
    return phase


def _format_seconds(seconds: float) -> str:
    """Format seconds into a human-readable ETA string with graduated rounding.

    Examples: "~7s remaining", "~25s remaining", "~2m 30s remaining",
              "~1h 15m remaining"
    """
    seconds = max(0, seconds)

    if seconds < 10:
        # Round to nearest 1s for short ETAs
        s = max(1, round(seconds))
        return f"~{s}s remaining"
    elif seconds < 60:
        # Round to nearest 5s
        s = round(seconds / 5) * 5
        s = max(5, s)
        return f"~{s}s remaining"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        # Round seconds to nearest 10s for cleaner display
        secs = round(secs / 10) * 10
        if secs == 60:
            mins += 1
            secs = 0
        if secs > 0:
            return f"~{mins}m {secs}s remaining"
        return f"~{mins}m remaining"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        if mins > 0:
            return f"~{hours}h {mins}m remaining"
        return f"~{hours}h remaining"


@dataclass
class ETACalculator:
    """Calculates ETA for scan progress using Exponential Moving Average.

    Call update() on each progress tick. Read format_remaining() for display.
    The calculator automatically resets when the scan phase or total changes
    (e.g., movie scan switching from "Checking" to "Analyzing").
    """

    alpha: float = 0.15
    min_samples: int = 5
    min_update_interval: float = 2.0

    # Internal state
    _ema_duration: float = field(default=0.0, init=False)
    _samples: int = field(default=0, init=False)
    _last_time: float | None = field(default=None, init=False)
    _last_phase_key: str = field(default="", init=False)
    _last_total: int = field(default=0, init=False)
    _remaining: float | None = field(default=None, init=False)
    _last_display_time: float = field(default=0.0, init=False)
    _last_display_text: str = field(default="", init=False)

    def reset(self) -> None:
        """Full reset for a new scan."""
        self._ema_duration = 0.0
        self._samples = 0
        self._last_time = None
        self._last_phase_key = ""
        self._last_total = 0
        self._remaining = None
        self._last_display_time = 0.0
        self._last_display_text = ""

    def _reset_phase(self) -> None:
        """Reset EMA state for a new phase, keeping display timing."""
        self._ema_duration = 0.0
        self._samples = 0
        self._last_time = None
        self._remaining = None

    def update(self, phase: str, current: int, total: int) -> None:
        """Record a progress tick and update the EMA estimate.

        Args:
            phase: Progress phase string (e.g., "Checking: Movie Name").
            current: Current item number (1-based).
            total: Total items in this phase.
        """
        now = time.monotonic()
        phase_key = _extract_phase_key(phase)

        # Detect phase change or total change → reset EMA
        if phase_key != self._last_phase_key or total != self._last_total:
            self._reset_phase()
            self._last_phase_key = phase_key
            self._last_total = total

        # Calculate per-item duration from successive ticks
        if self._last_time is not None:
            dt = now - self._last_time
            # Ignore unreasonably long gaps (>30s likely a pause/retry)
            if dt < 30.0:
                if self._samples == 0:
                    self._ema_duration = dt
                else:
                    self._ema_duration = self.alpha * dt + (1 - self.alpha) * self._ema_duration
                self._samples += 1

        self._last_time = now

        # Calculate remaining time
        if self._samples >= self.min_samples and total > 0:
            items_left = total - current
            self._remaining = self._ema_duration * items_left
        else:
            self._remaining = None

    @property
    def remaining_seconds(self) -> float | None:
        """Get estimated remaining seconds, or None if not enough data."""
        return self._remaining

    def format_remaining(self) -> str:
        """Get formatted ETA string with flicker protection.

        Returns display text like "~2m 30s remaining", "Calculating...",
        or "" (empty for indeterminate progress).
        """
        now = time.monotonic()

        # Not enough data yet but we have started
        if self._remaining is None:
            if self._samples > 0:
                text = "Calculating..."
            else:
                return ""
        elif self._remaining < 1.0:
            text = "Almost done..."
        else:
            text = _format_seconds(self._remaining)

        # Flicker protection: only update display every min_update_interval
        if self._last_display_text and now - self._last_display_time < self.min_update_interval:
            return self._last_display_text

        self._last_display_time = now
        self._last_display_text = text
        return text
