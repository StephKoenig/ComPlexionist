# ComPlexionist v2.0.110 - Collection Organization & Performance

**Release Date:** March 2026
**Version:** 2.0.110

---

## Overview

This release adds smart collection organization detection, showing complete collections that need organizing and providing an "Organised" status indicator. The organize dialog is significantly faster thanks to targeted UI updates, and unused overview data has been removed from the cache to reduce size.

---

## New Features

### Complete Collection Detection
Collections where you own every movie now appear in results when their files are scattered across different folders:
- **"Complete X of X"** (orange) subtitle indicates a fully-owned but disorganized collection
- Collections where all movies are already in the same folder are not shown
- Ignore/hide still works on complete collections

### Organization Status Indicator
Collections with 2+ owned movies now show organization status in the subtitle:
- **Organize** (orange button) — movies are in different folders, click to organize
- **Organised** (green tick) — movies are already grouped in the same folder
- The folder doesn't have to be named after the collection — just needs to be the same folder

### Improved Organize Dialog
- **Instant open** — dialog appears immediately with file list (no waiting for filesystem checks)
- **Background safety checks** — file existence, permissions, and conflict checks run in background with progress indicator
- **In-dialog move progress** — progress bar and per-file status ("Moving: filename.mkv") shown in the same dialog
- **Immediate button feedback** — "Move Files" changes to "Moving..." and disables instantly on click
- **Note about scan** — dialog reminds users that changes will be reflected after the next scan

---

## Improvements

### Performance
- **Targeted UI updates** — organize dialog uses `dialog.update()` instead of `page.update()`, avoiding full-page re-renders of hundreds of result controls. Dialog open, close, and all interactions are now near-instant.
- **Pre-created overlay controls** — dialog and snackbar are added to the page overlay once during screen build, eliminating repeated full-page updates
- **Modal dialog** — organize dialog now captures focus immediately, preventing missed clicks

### Cache Size Reduction
- Removed unused `overview` fields from TMDB movies/collections, TVDB episodes/series, and gap models
- These fields were cached but never displayed anywhere (GUI, CLI, CSV, JSON)
- Existing cache entries with overview data still load fine (Pydantic ignores extra fields)
- New cache entries will be smaller

### Dependencies
- flet 0.80.5 → 0.81.0
- rich 14.3.2 → 14.3.3
- ruff 0.15.2 → 0.15.4
- python-dotenv 1.2.1 → 1.2.2

---

## Bug Fixes

- Fixed organize button appearing on collections where all movies are in the same subfolder (e.g., movies directly in a collection folder without individual movie subfolders)
- Fixed "Move Files" button not responding to clicks (event handler was being set from a background thread)
- Fixed double-click on "Move Files" causing errors when files were already moved by the first click

---

## Upgrade Notes

- No configuration changes needed
- Your cache will automatically benefit from smaller entries on next scan (old entries with overview data are still compatible)

---

## Support & Contributing

- **Issues:** [GitHub Issues](https://github.com/The-Ant-Forge/ComPlexionist/issues)
- **Repository:** [GitHub](https://github.com/The-Ant-Forge/ComPlexionist)

---

## License

MIT License - See [LICENSE](LICENSE) for details.
