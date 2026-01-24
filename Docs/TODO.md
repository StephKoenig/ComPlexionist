# ComPlexionist - Development TODO

## Current Focus: Phase 3 - Movie Gap Detection

- [ ] Create `MovieGapFinder` class in `gaps/movies.py`
- [ ] Build owned movie set from Plex (by TMDB ID)
- [ ] Query TMDB for collection membership for each movie
- [ ] Deduplicate collections (many movies share same collection)
- [ ] Fetch full collections from TMDB
- [ ] Filter out future releases (release_date > today)
- [ ] Compare and identify missing movies
- [ ] Generate missing movies report (grouped by collection)
- [ ] Wire into CLI `movies` command
- [ ] Add progress indicators

---

## Completed Phases

### Phase 0: Project Setup ✓
- [x] Initialize Python project with `pyproject.toml`
- [x] Set up virtual environment
- [x] Install core dependencies
- [x] Create package structure (`src/complexionist/`)
- [x] Create `.env.example`
- [x] Set up Ruff linting
- [x] Create CLI entry point

### Phase 1: Plex Integration ✓
- [x] Implement Plex authentication (token-based)
- [x] List available libraries
- [x] Extract movies with TMDB IDs
- [x] Extract TV shows with TVDB GUIDs
- [x] Extract episodes with season/episode numbers
- [x] Handle missing external IDs gracefully

### Phase 2: TMDB Integration ✓
- [x] Create TMDB API client
- [x] Implement movie details endpoint (get collection info)
- [x] Implement collection endpoint (get all movies)
- [x] Handle rate limiting with backoff utility

---

## Upcoming Phases

### Phase 4: TVDB Integration
- [ ] Create TVDB v4 API client
- [ ] Implement login/token flow (Bearer token)
- [ ] Implement series episodes endpoint (paginated)
- [ ] Handle rate limiting

### Phase 5: Episode Gap Detection
- [ ] Build owned episode map from Plex
- [ ] Parse multi-episode filenames (S02E01-02)
- [ ] Query TVDB for complete episode lists
- [ ] Filter: future, specials, very recent
- [ ] Compare and generate missing episodes report

### Phase 6: CLI Polish (v1.0)
- [ ] Wire gap detection into CLI commands
- [ ] JSON output format
- [ ] CSV output format
- [ ] Progress indicators with Rich
- [ ] Configuration file support
- [ ] Comprehensive error handling

### Phase 7: Caching (v1.1)
- [ ] Design cache storage (SQLite or JSON)
- [ ] Implement TTL-based caching
- [ ] `--no-cache` flag
- [ ] `cache --clear` command

### Phase 8: GUI (v2.0)
- [ ] Evaluate GUI options (PyQt, Textual, Web)
- [ ] Design UI/UX
- [ ] Implement GUI

---

## Documentation

- [x] README.md
- [x] Plex-Background.md
- [x] Reference-Analysis.md
- [x] Specification.md
- [x] Implementation-Plan.md
- [x] Completed.md (updated)
- [ ] User guide
- [ ] API key setup instructions
