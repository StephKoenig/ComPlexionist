"""TMDB (The Movie Database) API integration."""

from complexionist.tmdb.client import (
    TMDBAuthError,
    TMDBClient,
    TMDBError,
    TMDBNotFoundError,
    TMDBRateLimitError,
)
from complexionist.tmdb.models import (
    TMDBCollection,
    TMDBCollectionInfo,
    TMDBMovie,
    TMDBMovieDetails,
)

__all__ = [
    "TMDBClient",
    "TMDBError",
    "TMDBAuthError",
    "TMDBNotFoundError",
    "TMDBRateLimitError",
    "TMDBMovie",
    "TMDBMovieDetails",
    "TMDBCollection",
    "TMDBCollectionInfo",
]
