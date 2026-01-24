# ComPlexionist - Development TODO

## Project Setup

- [x] Initialize Git repository
- [x] Create GitHub repository
- [ ] Set up `.github/` folder (workflows, issue templates, etc.)
- [ ] Choose and configure tech stack
- [ ] Set up development environment
- [ ] Configure linting and formatting

## Research & Planning

- [x] Research Plex API and authentication
- [x] Research TMDB Collections API
- [x] Research TVDB Episodes API
- [x] Review reference implementations:
  - [x] Gaps (movie collection gap finder)
  - [x] WebTools-NG (general Plex tool)
  - [x] PlexMissingEpisodes (TV episode gaps)
- [ ] Finalize architecture decisions
- [ ] Decide on tech stack (Python recommended based on research)

## Core Features

### Authentication Module
- [ ] Implement Plex authentication (X-Plex-Token)
- [ ] Support username/password → token flow
- [ ] Implement TMDB API key handling
- [ ] Implement TVDB API key handling (v4 with Bearer token)
- [ ] Secure credential storage (.env or similar)

### Plex Integration
- [ ] Connect to Plex Media Server
- [ ] Fetch library sections
- [ ] Fetch movies with TMDB IDs from metadata
- [ ] Fetch TV shows with TVDB GUIDs from metadata
- [ ] Fetch episodes with season/episode numbers

### Movie Collection Gaps Feature
- [ ] Get all movies from Plex movie library
- [ ] For each movie with TMDB ID:
  - [ ] Query TMDB for movie details (includes `belongs_to_collection`)
  - [ ] If in collection, fetch full collection from TMDB
  - [ ] Compare collection movies against Plex library (by TMDB ID)
- [ ] Generate missing movies report
- [ ] Group results by collection

### TV Episode Gaps Feature
- [ ] Get all TV shows from Plex TV library
- [ ] For each show with TVDB GUID:
  - [ ] Query TVDB v4 for all episodes (paginated)
  - [ ] Filter: exclude unaired, optionally exclude specials (S00)
  - [ ] Compare against Plex episodes (by S##E## AND name)
  - [ ] Handle multi-episode files (parse filenames like S02E01-02)
- [ ] Generate missing episodes report
- [ ] Group results by show, then season

## User Interface

- [ ] Determine UI approach (CLI first, web UI later?)
- [ ] Design user flows
- [ ] Implement output formatting (simple vs detailed)
- [ ] Add filtering/sorting options
- [ ] Support show exclusion list

## Testing

- [ ] Set up testing framework
- [ ] Unit tests for API integrations
- [ ] Integration tests
- [ ] Mock data for development without live Plex server

## Documentation

- [x] Create README.md
- [x] Create Plex-Background.md
- [x] Create Reference-Analysis.md
- [ ] API documentation
- [ ] User guide
- [ ] Contributing guidelines

## Future Enhancements

- [ ] Caching for API responses
- [ ] Batch processing for large libraries
- [ ] Export reports (CSV, JSON)
- [ ] Watchlist integration
- [ ] Notifications for new releases in missing collections
- [ ] Support TMDB as alternative to TVDB for TV shows
