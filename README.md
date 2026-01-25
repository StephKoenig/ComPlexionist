# ComPlexionist

A tool to identify missing content in your Plex Media Server libraries.

## Features

### Movie Collection Gaps
Plex automatically creates Collections when you own movies that belong to a franchise (e.g., "Alien Collection", "Star Wars Collection"). However, Plex doesn't tell you which movies from those collections you're missing.

ComPlexionist solves this by:
- Scanning your Plex movie library collections
- Cross-referencing with TMDB (The Movie Database) to get the complete collection
- Listing all missing movies from each collection

### TV Episode Gaps
For TV show libraries, ComPlexionist identifies missing episodes:
- Scans your Plex TV library for series
- Cross-references with TVDB for complete episode listings
- Reports missing episodes by season
- Handles multi-episode files (S02E01-02, S02E01-E02, etc.)

### Caching
API responses are cached to reduce redundant calls and speed up subsequent scans:
- TMDB movie/collection data: 7 days
- TVDB episode data: 24 hours
- Cache stored in `~/.complexionist/cache/` as human-readable JSON

## Prerequisites

- Python 3.11+
- Plex Media Server with configured libraries
- Plex authentication token ([how to find](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/))
- TMDB API key ([register free](https://www.themoviedb.org/settings/api))
- TVDB API key ([register](https://thetvdb.com/api-information))

## Installation

```bash
# Clone the repository
git clone https://github.com/StephKoenig/ComPlexionist.git
cd ComPlexionist

# Create virtual environment and install
python -m venv .venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -e ".[dev]"
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
PLEX_URL=http://your-plex-server:32400
PLEX_TOKEN=your-plex-token
TMDB_API_KEY=your-tmdb-api-key
TVDB_API_KEY=your-tvdb-api-key
```

### Configuration File (optional)
Create a config file for additional settings:

```bash
complexionist config init
```

This creates `~/.complexionist/config.yaml`:

```yaml
plex:
  url: "${PLEX_URL}"
  token: "${PLEX_TOKEN}"

tmdb:
  api_key: "${TMDB_API_KEY}"

tvdb:
  api_key: "${TVDB_API_KEY}"

options:
  exclude_future: true
  exclude_specials: true
  recent_threshold_hours: 24
  min_collection_size: 2

exclusions:
  shows:
    # - "Daily Talk Show"
  collections:
    # - "Anthology Collection"
```

## Usage

### Find Missing Movies

```bash
# Scan movie library for collection gaps
complexionist movies

# Include unreleased movies
complexionist movies --include-future

# Output as JSON
complexionist movies --format json

# Skip small collections (less than 3 movies)
complexionist movies --min-collection-size 3
```

### Find Missing Episodes

```bash
# Scan TV library for episode gaps
complexionist episodes

# Include specials (Season 0)
complexionist episodes --include-specials

# Include unaired episodes
complexionist episodes --include-future

# Exclude specific shows
complexionist episodes --exclude-show "Daily Talk Show"

# Skip recently aired (within 48 hours)
complexionist episodes --recent-threshold 48
```

### Scan Both Libraries

```bash
complexionist scan
```

### Cache Management

```bash
# View cache statistics
complexionist cache stats

# Clear all cached data
complexionist cache clear
```

### Configuration Commands

```bash
# Show current configuration
complexionist config show

# Show config file paths
complexionist config path

# Create default config file
complexionist config init
```

### Common Options

```bash
# Quiet mode (no progress indicators)
complexionist -q movies

# Verbose mode
complexionist -v movies

# Bypass cache
complexionist movies --no-cache

# Output formats: text (default), json, csv
complexionist movies --format json
complexionist episodes --format csv
```

## Example Output

```
Movie Collection Gaps - Movies

Summary:
  Movies scanned: 1,234
  In collections: 89
  Collections with gaps: 12

Alien Collection (missing 2 of 6):
  - Alien³ (1992)
  - Alien Resurrection (1997)

Terminator Collection (missing 1 of 6):
  - Terminator: Dark Fate (2019)
```

## Documentation

- [Plex Background Research](Docs/Plex-Background.md) - Technical details about Plex API
- [Specification](Docs/Specification.md) - Feature specs and architecture
- [Completed Work](Docs/Completed.md) - Development history

## License

MIT

## Acknowledgments

- [Plex](https://www.plex.tv/) - Media server platform
- [TMDB](https://www.themoviedb.org/) - Movie metadata
- [TVDB](https://thetvdb.com/) - TV show metadata
- [python-plexapi](https://github.com/pkkid/python-plexapi) - Python bindings for Plex API
