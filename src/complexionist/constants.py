"""Shared constants for ComPlexionist.

Centralizes constants used across CLI and GUI modules.
"""

from __future__ import annotations

# =============================================================================
# Brand Colors
# =============================================================================

# Plex brand gold/yellow color
PLEX_GOLD = "#F7C600"

# Alias for backward compatibility and clarity
PLEX_YELLOW = PLEX_GOLD

# =============================================================================
# Score Thresholds
# =============================================================================

# Thresholds for completion score display (percentage)
SCORE_THRESHOLD_GOOD = 90  # Score >= 90% is "good" (green)
SCORE_THRESHOLD_WARNING = 70  # Score >= 70% is "warning" (yellow/orange)
# Score < 70% is "bad" (red)

# Cache hit rate threshold for "good" display (percentage)
CACHE_HIT_RATE_GOOD = 50  # > 50% is good (green), <= 50% is warning (orange)


def get_score_rating(score: float) -> str:
    """Get a rating category for a completion score.

    Args:
        score: Completion percentage (0-100).

    Returns:
        Rating string: "good", "warning", or "bad".
    """
    if score >= SCORE_THRESHOLD_GOOD:
        return "good"
    elif score >= SCORE_THRESHOLD_WARNING:
        return "warning"
    return "bad"
