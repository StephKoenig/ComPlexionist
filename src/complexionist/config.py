"""Configuration management for ComPlexionist."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class PlexConfig(BaseModel):
    """Plex server configuration."""

    url: str | None = None
    token: str | None = None


class TMDBConfig(BaseModel):
    """TMDB API configuration."""

    api_key: str | None = None


class TVDBConfig(BaseModel):
    """TVDB API configuration."""

    api_key: str | None = None
    pin: str | None = None


class OptionsConfig(BaseModel):
    """General options configuration."""

    exclude_future: bool = True
    exclude_specials: bool = True
    recent_threshold_hours: int = 24
    min_collection_size: int = 2


class ExclusionsConfig(BaseModel):
    """Content exclusion configuration."""

    shows: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    """Application configuration."""

    plex: PlexConfig = Field(default_factory=PlexConfig)
    tmdb: TMDBConfig = Field(default_factory=TMDBConfig)
    tvdb: TVDBConfig = Field(default_factory=TVDBConfig)
    options: OptionsConfig = Field(default_factory=OptionsConfig)
    exclusions: ExclusionsConfig = Field(default_factory=ExclusionsConfig)


# Global config instance
_config: AppConfig | None = None


def get_config_paths() -> list[Path]:
    """Get list of config file paths to search, in priority order.

    Returns:
        List of paths to check for config files.
    """
    paths = []

    # Current directory config (highest priority)
    paths.append(Path.cwd() / "config.yaml")
    paths.append(Path.cwd() / "config.yml")
    paths.append(Path.cwd() / ".complexionist.yaml")
    paths.append(Path.cwd() / ".complexionist.yml")

    # User config directory
    config_dir = Path.home() / ".complexionist"
    paths.append(config_dir / "config.yaml")
    paths.append(config_dir / "config.yml")

    return paths


def find_config_file() -> Path | None:
    """Find the first existing config file.

    Returns:
        Path to config file if found, None otherwise.
    """
    for path in get_config_paths():
        if path.exists():
            return path
    return None


def _expand_env_vars(value: Any) -> Any:
    """Recursively expand environment variables in config values.

    Supports ${VAR} and $VAR syntax.

    Args:
        value: Config value (string, dict, list, or other).

    Returns:
        Value with environment variables expanded.
    """
    if isinstance(value, str):
        # Pattern matches ${VAR} or $VAR
        pattern = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

        def replace(match: re.Match[str]) -> str:
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, "")

        return pattern.sub(replace, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from file.

    Args:
        path: Explicit path to config file. If None, searches default locations.

    Returns:
        Loaded configuration with environment variables expanded.
    """
    global _config

    # Find config file
    if path is None:
        path = find_config_file()

    if path is None or not path.exists():
        # No config file, return defaults
        _config = AppConfig()
        return _config

    # Load YAML
    with open(path, encoding="utf-8") as f:
        raw_config = yaml.safe_load(f) or {}

    # Expand environment variables
    expanded_config = _expand_env_vars(raw_config)

    # Parse into config model
    _config = AppConfig.model_validate(expanded_config)
    return _config


def get_config() -> AppConfig:
    """Get the current configuration.

    Loads from file if not already loaded.

    Returns:
        Current application configuration.
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Reset the cached configuration.

    Useful for testing or when config file changes.
    """
    global _config
    _config = None


def get_config_dir() -> Path:
    """Get the user config directory.

    Creates the directory if it doesn't exist.

    Returns:
        Path to config directory.
    """
    config_dir = Path.home() / ".complexionist"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def save_default_config(path: Path | None = None) -> Path:
    """Save a default config file with documentation.

    Args:
        path: Where to save. Defaults to ~/.complexionist/config.yaml.

    Returns:
        Path to saved config file.
    """
    if path is None:
        path = get_config_dir() / "config.yaml"

    default_config = """\
# ComPlexionist Configuration
# See: https://github.com/StephKoenig/ComPlexionist

# Plex Media Server settings
# You can use environment variables with ${VAR} syntax
plex:
  url: "${PLEX_URL}"           # e.g., http://192.168.1.100:32400
  token: "${PLEX_TOKEN}"       # X-Plex-Token from Plex settings

# TMDB (The Movie Database) API
# Get your API key at: https://www.themoviedb.org/settings/api
tmdb:
  api_key: "${TMDB_API_KEY}"

# TVDB API
# Get your API key at: https://thetvdb.com/api-information
tvdb:
  api_key: "${TVDB_API_KEY}"
  pin: ""                       # Optional subscriber PIN

# Default options (can be overridden via CLI flags)
options:
  exclude_future: true          # Exclude unreleased movies/episodes
  exclude_specials: true        # Exclude Season 0 (specials)
  recent_threshold_hours: 24    # Skip episodes aired within this many hours
  min_collection_size: 2        # Only show collections with N+ movies

# Content exclusions
exclusions:
  # Shows to skip when checking for missing episodes
  # Use exact show titles as they appear in Plex
  shows:
    # - "Daily Talk Show"
    # - "News Program"

  # Collections to skip when checking for missing movies
  collections:
    # - "Anthology Collection"
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(default_config)

    return path
