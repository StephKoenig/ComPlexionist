"""File-based caching for API responses.

Cache structure:
    ~/.complexionist/cache/
    ├── tmdb/
    │   ├── movies/
    │   │   └── {movie_id}.json
    │   └── collections/
    │       └── {collection_id}.json
    └── tvdb/
        └── episodes/
            └── {series_id}.json

Each JSON file contains:
    {
        "_cache_meta": {
            "cached_at": "2025-01-25T10:00:00Z",
            "expires_at": "2025-02-01T10:00:00Z",
            "ttl_hours": 168,
            "description": "Human-readable description"
        },
        "data": { ... actual cached data ... }
    }
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Default TTLs in hours
TMDB_MOVIE_TTL_HOURS = 168  # 7 days
TMDB_COLLECTION_TTL_HOURS = 168  # 7 days
TVDB_EPISODES_TTL_HOURS = 24  # 24 hours


@dataclass
class CacheStats:
    """Statistics about the cache."""

    total_entries: int
    total_size_bytes: int
    tmdb_movies: int
    tmdb_collections: int
    tvdb_episodes: int
    oldest_entry: datetime | None
    newest_entry: datetime | None

    @property
    def total_size_mb(self) -> float:
        """Total size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)

    @property
    def total_size_kb(self) -> float:
        """Total size in kilobytes."""
        return self.total_size_bytes / 1024


def get_cache_dir() -> Path:
    """Get the cache directory.

    Returns:
        Path to cache directory (~/.complexionist/cache).
    """
    cache_dir = Path.home() / ".complexionist" / "cache"
    return cache_dir


class Cache:
    """File-based cache for API responses.

    Uses JSON files organized by namespace (tmdb/tvdb) and type
    (movies, collections, episodes). Each cache entry includes
    metadata for TTL and human-readable descriptions.
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        enabled: bool = True,
    ) -> None:
        """Initialize the cache.

        Args:
            cache_dir: Custom cache directory. Defaults to ~/.complexionist/cache.
            enabled: Whether caching is enabled. If False, all operations are no-ops.
        """
        self.enabled = enabled
        self.cache_dir = cache_dir or get_cache_dir()

    def _get_path(self, namespace: str, category: str, key: str) -> Path:
        """Get the file path for a cache entry.

        Args:
            namespace: Top-level namespace (e.g., "tmdb", "tvdb").
            category: Category within namespace (e.g., "movies", "collections").
            key: Unique key for the entry (e.g., movie ID).

        Returns:
            Path to the cache file.
        """
        return self.cache_dir / namespace / category / f"{key}.json"

    def get(self, namespace: str, category: str, key: str) -> dict[str, Any] | None:
        """Get a cached entry if it exists and hasn't expired.

        Args:
            namespace: Top-level namespace (e.g., "tmdb", "tvdb").
            category: Category within namespace (e.g., "movies", "collections").
            key: Unique key for the entry.

        Returns:
            Cached data dict if found and valid, None otherwise.
        """
        if not self.enabled:
            return None

        path = self._get_path(namespace, category, key)

        if not path.exists():
            return None

        try:
            with open(path, encoding="utf-8") as f:
                entry = json.load(f)

            # Check expiration
            meta = entry.get("_cache_meta", {})
            expires_at_str = meta.get("expires_at")

            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now(UTC) > expires_at:
                    # Expired - delete and return None
                    path.unlink(missing_ok=True)
                    return None

            return entry.get("data")

        except (json.JSONDecodeError, OSError, ValueError):
            # Corrupted or unreadable - delete it
            path.unlink(missing_ok=True)
            return None

    def set(
        self,
        namespace: str,
        category: str,
        key: str,
        data: dict[str, Any],
        ttl_hours: int,
        description: str = "",
    ) -> None:
        """Store data in the cache.

        Args:
            namespace: Top-level namespace (e.g., "tmdb", "tvdb").
            category: Category within namespace (e.g., "movies", "collections").
            key: Unique key for the entry.
            data: Data to cache.
            ttl_hours: Time-to-live in hours.
            description: Human-readable description for the cache entry.
        """
        if not self.enabled:
            return

        path = self._get_path(namespace, category, key)

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=ttl_hours)

        entry = {
            "_cache_meta": {
                "cached_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "ttl_hours": ttl_hours,
                "description": description,
            },
            "data": data,
        }

        # Write atomically by writing to temp file first
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2, default=str)
            temp_path.replace(path)
        except OSError:
            # Clean up temp file if something went wrong
            temp_path.unlink(missing_ok=True)
            raise

    def delete(self, namespace: str, category: str, key: str) -> bool:
        """Delete a specific cache entry.

        Args:
            namespace: Top-level namespace.
            category: Category within namespace.
            key: Unique key for the entry.

        Returns:
            True if entry was deleted, False if it didn't exist.
        """
        path = self._get_path(namespace, category, key)

        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self, namespace: str | None = None) -> int:
        """Clear cache entries.

        Args:
            namespace: If provided, only clear entries in this namespace.
                If None, clear all entries.

        Returns:
            Number of entries deleted.
        """
        count = 0

        if not self.cache_dir.exists():
            return count

        if namespace:
            # Clear specific namespace
            ns_dir = self.cache_dir / namespace
            if ns_dir.exists():
                for json_file in ns_dir.rglob("*.json"):
                    json_file.unlink()
                    count += 1
        else:
            # Clear all
            for json_file in self.cache_dir.rglob("*.json"):
                json_file.unlink()
                count += 1

        # Clean up empty directories
        self._cleanup_empty_dirs()

        return count

    def _cleanup_empty_dirs(self) -> None:
        """Remove empty directories in the cache."""
        if not self.cache_dir.exists():
            return

        # Walk bottom-up to remove empty directories
        for dirpath in sorted(self.cache_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()

    def stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats with counts and size information.
        """
        total_entries = 0
        total_size = 0
        tmdb_movies = 0
        tmdb_collections = 0
        tvdb_episodes = 0
        oldest: datetime | None = None
        newest: datetime | None = None

        if not self.cache_dir.exists():
            return CacheStats(
                total_entries=0,
                total_size_bytes=0,
                tmdb_movies=0,
                tmdb_collections=0,
                tvdb_episodes=0,
                oldest_entry=None,
                newest_entry=None,
            )

        for json_file in self.cache_dir.rglob("*.json"):
            total_entries += 1
            total_size += json_file.stat().st_size

            # Count by category
            rel_path = json_file.relative_to(self.cache_dir)
            parts = rel_path.parts

            if len(parts) >= 2:
                namespace, category = parts[0], parts[1]
                if namespace == "tmdb":
                    if category == "movies":
                        tmdb_movies += 1
                    elif category == "collections":
                        tmdb_collections += 1
                elif namespace == "tvdb":
                    if category == "episodes":
                        tvdb_episodes += 1

            # Track oldest/newest
            try:
                with open(json_file, encoding="utf-8") as f:
                    entry = json.load(f)
                cached_at_str = entry.get("_cache_meta", {}).get("cached_at")
                if cached_at_str:
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if oldest is None or cached_at < oldest:
                        oldest = cached_at
                    if newest is None or cached_at > newest:
                        newest = cached_at
            except (json.JSONDecodeError, OSError, ValueError):
                continue

        return CacheStats(
            total_entries=total_entries,
            total_size_bytes=total_size,
            tmdb_movies=tmdb_movies,
            tmdb_collections=tmdb_collections,
            tvdb_episodes=tvdb_episodes,
            oldest_entry=oldest,
            newest_entry=newest,
        )

    def get_expired_count(self) -> int:
        """Count expired entries that haven't been cleaned up yet.

        Returns:
            Number of expired entries.
        """
        count = 0
        now = datetime.now(UTC)

        if not self.cache_dir.exists():
            return count

        for json_file in self.cache_dir.rglob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    entry = json.load(f)
                expires_at_str = entry.get("_cache_meta", {}).get("expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if now > expires_at:
                        count += 1
            except (json.JSONDecodeError, OSError, ValueError):
                count += 1  # Corrupted files count as expired

        return count

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed.
        """
        count = 0
        now = datetime.now(UTC)

        if not self.cache_dir.exists():
            return count

        for json_file in self.cache_dir.rglob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    entry = json.load(f)
                expires_at_str = entry.get("_cache_meta", {}).get("expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if now > expires_at:
                        json_file.unlink()
                        count += 1
            except (json.JSONDecodeError, OSError, ValueError):
                # Corrupted - delete it
                json_file.unlink(missing_ok=True)
                count += 1

        self._cleanup_empty_dirs()
        return count
