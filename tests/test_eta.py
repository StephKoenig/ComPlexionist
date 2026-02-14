"""Tests for the ETA countdown calculator."""

from __future__ import annotations

from unittest.mock import patch

from complexionist.eta import ETACalculator, _extract_phase_key, _format_seconds


class TestExtractPhaseKey:
    """Tests for _extract_phase_key()."""

    def test_with_colon_separator(self):
        assert _extract_phase_key("Checking: Movie Name") == "Checking"

    def test_with_colon_separator_analyzing(self):
        assert _extract_phase_key("Analyzing: The Big Lebowski") == "Analyzing"

    def test_without_colon(self):
        assert _extract_phase_key("Processing") == "Processing"

    def test_empty_string(self):
        assert _extract_phase_key("") == ""

    def test_multiple_colons(self):
        assert _extract_phase_key("Phase: Name: Extra") == "Phase"


class TestFormatSeconds:
    """Tests for _format_seconds()."""

    def test_zero_seconds(self):
        assert _format_seconds(0) == "~1s remaining"

    def test_small_seconds(self):
        assert _format_seconds(7.3) == "~7s remaining"

    def test_rounds_to_5s_over_10(self):
        assert _format_seconds(23) == "~25s remaining"

    def test_rounds_to_5s_exact(self):
        assert _format_seconds(30) == "~30s remaining"

    def test_one_minute(self):
        assert _format_seconds(60) == "~1m remaining"

    def test_minutes_and_seconds(self):
        assert _format_seconds(150) == "~2m 30s remaining"

    def test_rounds_seconds_in_minutes(self):
        # 95 seconds = 1m 35s, rounds to 1m 40s
        assert _format_seconds(95) == "~1m 40s remaining"

    def test_one_hour(self):
        assert _format_seconds(3600) == "~1h remaining"

    def test_hours_and_minutes(self):
        assert _format_seconds(4500) == "~1h 15m remaining"

    def test_negative_clamps_to_zero(self):
        assert _format_seconds(-5) == "~1s remaining"


class TestETACalculator:
    """Tests for ETACalculator."""

    def _make_calculator(self, **kwargs):
        """Create a calculator with flicker protection disabled for testing."""
        calc = ETACalculator(min_update_interval=0.0, **kwargs)
        return calc

    def test_no_estimate_before_min_samples(self):
        calc = self._make_calculator(min_samples=5)
        # Simulate ticks with controlled time
        times = iter([1.0, 1.5, 2.0, 2.5, 3.0])
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 5):
                calc.update(f"Checking: Item {i}", i, 100)
        assert calc.remaining_seconds is None

    def test_estimate_after_min_samples(self):
        calc = self._make_calculator(min_samples=3)
        # Each tick is 0.5s apart, so EMA converges toward 0.5s/item
        times = [float(i) * 0.5 for i in range(6)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 6):
                calc.update(f"Checking: Item {i}", i, 100)
        assert calc.remaining_seconds is not None
        assert calc.remaining_seconds > 0

    def test_phase_transition_resets(self):
        calc = self._make_calculator(min_samples=2)
        # Build up an estimate in phase 1
        times = [float(i) * 0.5 for i in range(5)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 5):
                calc.update(f"Checking: Item {i}", i, 10)
        assert calc.remaining_seconds is not None

        # Switch to new phase — should reset
        with patch("complexionist.eta.time.monotonic", return_value=10.0):
            calc.update("Analyzing: Collection 1", 1, 5)
        assert calc.remaining_seconds is None

    def test_total_change_resets(self):
        calc = self._make_calculator(min_samples=2)
        # Build up estimate
        times = [float(i) * 0.5 for i in range(5)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 5):
                calc.update(f"Analyzing: Show {i}", i, 50)
        assert calc.remaining_seconds is not None

        # Same phase key but different total — reset
        with patch("complexionist.eta.time.monotonic", return_value=10.0):
            calc.update("Analyzing: Show 1", 1, 200)
        assert calc.remaining_seconds is None

    def test_indeterminate_returns_empty(self):
        calc = self._make_calculator()
        # No updates at all
        assert calc.format_remaining() == ""

    def test_calculating_before_enough_samples(self):
        calc = self._make_calculator(min_samples=5)
        # Need two ticks to get a duration sample (but still < min_samples)
        times = [0.0, 0.5, 1.0]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            calc.update("Checking: Item 1", 1, 100)
            calc.update("Checking: Item 2", 2, 100)
        # 1 sample, not enough for estimate → "Calculating..."
        result = calc.format_remaining()
        assert result == "Calculating..."

    def test_format_remaining_shows_eta(self):
        calc = self._make_calculator(min_samples=2)
        # 0.5s per item, 100 items, at item 10 → ~45s left
        times = [float(i) * 0.5 for i in range(12)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 11):
                calc.update(f"Checking: Item {i}", i, 100)
        result = calc.format_remaining()
        assert "remaining" in result

    def test_almost_done(self):
        calc = self._make_calculator(min_samples=2)
        # 0.1s per item, at item 99 of 100 → ~0.1s left
        times = [float(i) * 0.1 for i in range(102)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 100):
                calc.update(f"Checking: Item {i}", i, 100)
        result = calc.format_remaining()
        assert result == "Almost done..."

    def test_reset_clears_everything(self):
        calc = self._make_calculator(min_samples=2)
        times = [float(i) * 0.5 for i in range(5)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 5):
                calc.update(f"Checking: Item {i}", i, 10)
        assert calc.remaining_seconds is not None

        calc.reset()
        assert calc.remaining_seconds is None
        assert calc.format_remaining() == ""

    def test_flicker_protection(self):
        calc = ETACalculator(min_samples=2, min_update_interval=5.0)
        # Build estimate
        times = [float(i) * 0.5 for i in range(6)]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 6):
                calc.update(f"Checking: Item {i}", i, 100)

        # First format call at t=3.0 — sets the display
        with patch("complexionist.eta.time.monotonic", return_value=3.0):
            first_text = calc.format_remaining()

        # Artificially change the remaining to something different
        calc._remaining = 999.0

        # Second call at t=4.0 (within 5s interval) — should return cached text
        with patch("complexionist.eta.time.monotonic", return_value=4.0):
            second_text = calc.format_remaining()
        assert second_text == first_text

        # Third call at t=9.0 (past interval) — should update
        with patch("complexionist.eta.time.monotonic", return_value=9.0):
            third_text = calc.format_remaining()
        assert third_text != first_text

    def test_ignores_long_gaps(self):
        calc = self._make_calculator(min_samples=2)
        # Normal ticks, then a 60s gap (likely a pause), then normal again
        times = [0.0, 0.5, 1.0, 61.0, 61.5, 62.0]
        with patch("complexionist.eta.time.monotonic", side_effect=times):
            for i in range(1, 7):
                calc.update(f"Checking: Item {i}", i, 100)
        # EMA should not be inflated by the 60s gap
        assert calc._ema_duration < 5.0
