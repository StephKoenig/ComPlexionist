# ComPlexionist v2.0.141 - Resolution Badges & Performance

**Release Date:** April 2026
**Version:** 2.0.141

---

## Overview

This release adds resolution and codec badges to movie and TV results, so you can assess media quality at a glance. Movies and shows now display their video resolution (720p, 1080p, 4K) and codec (H.264, HEVC, AV1) as pill badges alongside titles. The TMDB collection lookup is now parallelised for faster movie scans, and a 24-hour grace period prevents newly-aired content from showing as missing before it's actually available.

---

## New Features

### Resolution & Codec Badges
- Owned movies and TV shows now display resolution and codec as pill badges (e.g., `1080p` `HEVC`)
- Resolution is extracted from the last media entry in Plex (most recently added version)
- Codec names are normalised for readability (h264 → H.264, hevc → HEVC, av1 → AV1)
- Badges appear in GUI results, CLI output, and CSV/JSON exports
- Helps operators identify low-quality copies that may need upgrading

### 24-Hour Grace Period
- Content released/aired today is no longer flagged as missing
- Adds a 24-hour buffer to account for timezone differences and indexer delays
- Episodes and movies must be at least 1 day old before appearing as gaps

---

## Improvements

### Performance
- **Parallel TMDB lookups** — Movie collection checks now use 2 parallel workers with rate-limited API calls, significantly speeding up movie scans
- **Thread-safe statistics** — Scan counters now use proper locking for accurate stats during parallel operations
- **Smarter cache stagger** — Cached movies skip the rate-limit delay entirely, so only real API calls are throttled

### Dependencies
- flet 0.83.0 → 0.84.0
- click 8.3.1 → 8.3.2
- rich 14.3.3 → 14.3.4
- mypy 1.19.1 → 1.20.0
- ruff 0.15.6 → 0.15.10
- pytest 9.0.2 → 9.0.3
- requests ≥ 2.33.0, pygments ≥ 2.20.0 (security fixes)

---

## Bug Fixes

- Fixed TMDB parallel lookup stalling during the submission phase due to a blocking sleep in the main thread
- Fixed Dependabot security alerts for requests (insecure temp file reuse) and pygments (ReDoS)

---

## Upgrade Notes

- No configuration changes needed
- Cache files from previous versions remain compatible
- The 24-hour grace period applies automatically — no setting to configure

---

## Support & Contributing

- **Issues:** [GitHub Issues](https://github.com/The-Ant-Forge/ComPlexionist/issues)
- **Repository:** [GitHub](https://github.com/The-Ant-Forge/ComPlexionist)

---

## License

MIT License - See [LICENSE](LICENSE) for details.
