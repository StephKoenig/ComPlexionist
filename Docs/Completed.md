# ComPlexionist - Completed Work

This file is a durable record of finished work. Each entry captures what shipped, why it mattered, and where it lives.

See `TODO.md` for forward-looking work items.

---

## Project Setup and Documentation (2025-01-24)

**Why:** Establish project foundation with research and documentation before implementation.

**What we did:**
- Created `README.md` with project overview and feature descriptions
- Created `Docs/Plex-Background.md` with comprehensive Plex API research:
  - Authentication methods (X-Plex-Token, JWT, PIN flow)
  - Library architecture and content separation
  - Collections API and the "missing movies" problem
  - TV show hierarchy (Show > Season > Episode)
  - External data sources (TMDB for movies, TVDB for TV)
  - python-plexapi library overview
- Created `Docs/TODO.md` with development task breakdown
- Adapted `agents.md` from TVRenamer project for ComPlexionist workflow

**Key files:**
- `README.md`
- `Docs/Plex-Background.md`
- `Docs/TODO.md`
- `agents.md`

---

## Reference Implementation Analysis (2025-01-24)

**Why:** Understand how existing tools solve similar problems to inform our architecture decisions.

**What we analyzed:**

### Gaps (Movie Collections)
- Java Spring Boot app for finding missing movies in Plex collections
- Uses TMDB API to get complete collection membership
- Key insight: Match movies by TMDB ID, not name
- Key data: `BasicMovie` (Plex) vs `MovieFromCollection` (TMDB)
- Status: No longer maintained, but approach is solid

### WebTools-NG (General Plex Tool)
- Vue.js/Electron app for Plex server management
- Primarily an export tool, NOT a missing content detector
- Limited usefulness for our specific features

### PlexMissingEpisodes (TV Episodes)
- PowerShell script for finding missing TV episodes
- Uses TVDB v4 API for episode listings
- Key insights:
  - Use TVDB GUID from Plex metadata to link shows
  - Handle multi-episode files via filename parsing (S02E01-02)
  - Filter out specials (S00), unaired, and very recent episodes
  - Match by episode number AND name for accuracy
- Output: Simple (`Show - S01E01 - Title`) or detailed (grouped by show/season)

**Recommendations documented:**
- Python recommended (python-plexapi library)
- TMDB for movies (has collection data)
- TVDB v4 for TV (comprehensive episode data)
- CLI-first approach, optional web UI later

**Key files:**
- `Docs/Reference-Analysis.md`
