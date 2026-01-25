"""Data models for gap detection results."""

from datetime import date

from pydantic import BaseModel, Field


class MissingMovie(BaseModel):
    """A movie that's missing from the user's library."""

    tmdb_id: int
    title: str
    release_date: date | None = None
    year: int | None = None
    overview: str = ""

    @property
    def display_title(self) -> str:
        """Get the title with year for display."""
        if self.year:
            return f"{self.title} ({self.year})"
        return self.title


class CollectionGap(BaseModel):
    """A collection with missing movies."""

    collection_id: int
    collection_name: str
    total_movies: int
    owned_movies: int
    missing_movies: list[MissingMovie] = Field(default_factory=list)

    @property
    def missing_count(self) -> int:
        """Number of missing movies."""
        return len(self.missing_movies)

    @property
    def completion_percent(self) -> float:
        """Percentage of collection owned."""
        if self.total_movies == 0:
            return 100.0
        return (self.owned_movies / self.total_movies) * 100


class MovieGapReport(BaseModel):
    """Full report of movie collection gaps."""

    library_name: str
    total_movies_scanned: int
    movies_with_tmdb_id: int
    movies_in_collections: int
    unique_collections: int
    collections_with_gaps: list[CollectionGap] = Field(default_factory=list)

    @property
    def total_missing(self) -> int:
        """Total number of missing movies across all collections."""
        return sum(gap.missing_count for gap in self.collections_with_gaps)

    @property
    def complete_collections(self) -> int:
        """Number of collections that are complete."""
        return self.unique_collections - len(self.collections_with_gaps)
