"""Data models for TMDB API responses."""

from datetime import date

from pydantic import BaseModel, Field


class TMDBMovie(BaseModel):
    """A movie from TMDB."""

    id: int
    title: str
    release_date: date | None = None
    overview: str = ""
    poster_path: str | None = None

    @property
    def year(self) -> int | None:
        """Get the release year."""
        return self.release_date.year if self.release_date else None

    @property
    def is_released(self) -> bool:
        """Check if the movie has been released."""
        if self.release_date is None:
            return False
        return self.release_date <= date.today()


class TMDBCollectionInfo(BaseModel):
    """Basic collection info from a movie response."""

    id: int
    name: str
    poster_path: str | None = None
    backdrop_path: str | None = None


class TMDBCollection(BaseModel):
    """A full collection with all movies."""

    id: int
    name: str
    overview: str = ""
    poster_path: str | None = None
    backdrop_path: str | None = None
    parts: list[TMDBMovie] = Field(default_factory=list)

    @property
    def movie_count(self) -> int:
        """Get the number of movies in the collection."""
        return len(self.parts)

    @property
    def released_movies(self) -> list[TMDBMovie]:
        """Get only released movies."""
        return [m for m in self.parts if m.is_released]


class TMDBMovieDetails(BaseModel):
    """Full movie details including collection membership."""

    id: int
    title: str
    release_date: date | None = None
    overview: str = ""
    poster_path: str | None = None
    belongs_to_collection: TMDBCollectionInfo | None = None

    @property
    def collection_id(self) -> int | None:
        """Get the collection ID if this movie belongs to one."""
        return self.belongs_to_collection.id if self.belongs_to_collection else None

    @property
    def collection_name(self) -> str | None:
        """Get the collection name if this movie belongs to one."""
        return self.belongs_to_collection.name if self.belongs_to_collection else None
