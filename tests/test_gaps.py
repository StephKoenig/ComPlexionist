"""Tests for the gap detection module."""

from datetime import date
from unittest.mock import MagicMock

from complexionist.gaps import (
    CollectionGap,
    MissingMovie,
    MovieGapFinder,
    MovieGapReport,
)
from complexionist.plex import PlexMovie
from complexionist.tmdb import TMDBCollection, TMDBMovie, TMDBMovieDetails


class TestGapModels:
    """Tests for gap detection data models."""

    def test_missing_movie_display_title_with_year(self) -> None:
        """Test display title includes year when available."""
        movie = MissingMovie(
            tmdb_id=123,
            title="Test Movie",
            year=2020,
        )
        assert movie.display_title == "Test Movie (2020)"

    def test_missing_movie_display_title_without_year(self) -> None:
        """Test display title without year."""
        movie = MissingMovie(
            tmdb_id=123,
            title="Test Movie",
        )
        assert movie.display_title == "Test Movie"

    def test_collection_gap_missing_count(self) -> None:
        """Test missing count calculation."""
        gap = CollectionGap(
            collection_id=1,
            collection_name="Test Collection",
            total_movies=5,
            owned_movies=3,
            missing_movies=[
                MissingMovie(tmdb_id=1, title="Movie 1"),
                MissingMovie(tmdb_id=2, title="Movie 2"),
            ],
        )
        assert gap.missing_count == 2

    def test_collection_gap_completion_percent(self) -> None:
        """Test completion percentage calculation."""
        gap = CollectionGap(
            collection_id=1,
            collection_name="Test Collection",
            total_movies=4,
            owned_movies=3,
            missing_movies=[MissingMovie(tmdb_id=1, title="Movie 1")],
        )
        assert gap.completion_percent == 75.0

    def test_collection_gap_completion_percent_empty(self) -> None:
        """Test completion percentage with zero total movies."""
        gap = CollectionGap(
            collection_id=1,
            collection_name="Empty Collection",
            total_movies=0,
            owned_movies=0,
            missing_movies=[],
        )
        assert gap.completion_percent == 100.0

    def test_movie_gap_report_total_missing(self) -> None:
        """Test total missing count across collections."""
        report = MovieGapReport(
            library_name="Movies",
            total_movies_scanned=100,
            movies_with_tmdb_id=95,
            movies_in_collections=50,
            unique_collections=10,
            collections_with_gaps=[
                CollectionGap(
                    collection_id=1,
                    collection_name="Collection 1",
                    total_movies=5,
                    owned_movies=3,
                    missing_movies=[
                        MissingMovie(tmdb_id=1, title="Movie 1"),
                        MissingMovie(tmdb_id=2, title="Movie 2"),
                    ],
                ),
                CollectionGap(
                    collection_id=2,
                    collection_name="Collection 2",
                    total_movies=3,
                    owned_movies=2,
                    missing_movies=[
                        MissingMovie(tmdb_id=3, title="Movie 3"),
                    ],
                ),
            ],
        )
        assert report.total_missing == 3

    def test_movie_gap_report_complete_collections(self) -> None:
        """Test count of complete collections."""
        report = MovieGapReport(
            library_name="Movies",
            total_movies_scanned=100,
            movies_with_tmdb_id=95,
            movies_in_collections=50,
            unique_collections=10,
            collections_with_gaps=[
                CollectionGap(
                    collection_id=1,
                    collection_name="Collection 1",
                    total_movies=5,
                    owned_movies=3,
                    missing_movies=[MissingMovie(tmdb_id=1, title="Movie 1")],
                ),
            ],
        )
        # 10 total - 1 with gaps = 9 complete
        assert report.complete_collections == 9


class TestMovieGapFinder:
    """Tests for the MovieGapFinder class."""

    def _create_mock_plex_client(
        self, movies: list[PlexMovie]
    ) -> MagicMock:
        """Create a mock Plex client."""
        mock_client = MagicMock()
        mock_client.get_movies.return_value = movies
        mock_client.get_movie_libraries.return_value = [
            MagicMock(title="Movies")
        ]
        return mock_client

    def _create_mock_tmdb_client(
        self,
        movie_collections: dict[int, int | None],
        collections: dict[int, TMDBCollection],
    ) -> MagicMock:
        """Create a mock TMDB client."""
        mock_client = MagicMock()

        def get_movie(movie_id: int) -> TMDBMovieDetails:
            collection_id = movie_collections.get(movie_id)
            collection_info = None
            if collection_id:
                collection_info = {
                    "id": collection_id,
                    "name": f"Collection {collection_id}",
                }
            return TMDBMovieDetails(
                id=movie_id,
                title=f"Movie {movie_id}",
                belongs_to_collection=collection_info,
            )

        def get_collection(collection_id: int) -> TMDBCollection:
            return collections[collection_id]

        mock_client.get_movie.side_effect = get_movie
        mock_client.get_collection.side_effect = get_collection

        return mock_client

    def test_find_gaps_empty_library(self) -> None:
        """Test with empty movie library."""
        plex = self._create_mock_plex_client([])
        tmdb = self._create_mock_tmdb_client({}, {})

        finder = MovieGapFinder(plex, tmdb)
        report = finder.find_gaps()

        assert report.total_movies_scanned == 0
        assert report.movies_with_tmdb_id == 0
        assert report.collections_with_gaps == []

    def test_find_gaps_no_collections(self) -> None:
        """Test when movies don't belong to any collections."""
        movies = [
            PlexMovie(rating_key="1", title="Movie 1", tmdb_id=100),
            PlexMovie(rating_key="2", title="Movie 2", tmdb_id=200),
        ]
        plex = self._create_mock_plex_client(movies)
        # Movies return no collections
        tmdb = self._create_mock_tmdb_client({100: None, 200: None}, {})

        finder = MovieGapFinder(plex, tmdb)
        report = finder.find_gaps()

        assert report.total_movies_scanned == 2
        assert report.movies_with_tmdb_id == 2
        assert report.movies_in_collections == 0
        assert report.collections_with_gaps == []

    def test_find_gaps_complete_collection(self) -> None:
        """Test when user owns all movies in a collection."""
        movies = [
            PlexMovie(rating_key="1", title="Movie 1", tmdb_id=100),
            PlexMovie(rating_key="2", title="Movie 2", tmdb_id=101),
        ]
        plex = self._create_mock_plex_client(movies)

        # Both movies belong to collection 1
        movie_collections = {100: 1, 101: 1}
        collections = {
            1: TMDBCollection(
                id=1,
                name="Complete Collection",
                parts=[
                    TMDBMovie(id=100, title="Movie 1", release_date=date(2020, 1, 1)),
                    TMDBMovie(id=101, title="Movie 2", release_date=date(2021, 1, 1)),
                ],
            ),
        }
        tmdb = self._create_mock_tmdb_client(movie_collections, collections)

        finder = MovieGapFinder(plex, tmdb)
        report = finder.find_gaps()

        assert report.unique_collections == 1
        assert report.collections_with_gaps == []

    def test_find_gaps_with_missing_movies(self) -> None:
        """Test when user is missing movies from a collection."""
        movies = [
            PlexMovie(rating_key="1", title="Alien", tmdb_id=348),
        ]
        plex = self._create_mock_plex_client(movies)

        movie_collections = {348: 8091}  # Alien Collection
        collections = {
            8091: TMDBCollection(
                id=8091,
                name="Alien Collection",
                parts=[
                    TMDBMovie(id=348, title="Alien", release_date=date(1979, 5, 25)),
                    TMDBMovie(id=679, title="Aliens", release_date=date(1986, 7, 18)),
                    TMDBMovie(id=8077, title="Alien 3", release_date=date(1992, 5, 22)),
                ],
            ),
        }
        tmdb = self._create_mock_tmdb_client(movie_collections, collections)

        finder = MovieGapFinder(plex, tmdb)
        report = finder.find_gaps()

        assert len(report.collections_with_gaps) == 1
        gap = report.collections_with_gaps[0]
        assert gap.collection_name == "Alien Collection"
        assert gap.owned_movies == 1
        assert gap.total_movies == 3
        assert gap.missing_count == 2
        assert {m.title for m in gap.missing_movies} == {"Aliens", "Alien 3"}

    def test_find_gaps_excludes_future_releases(self) -> None:
        """Test that future releases are excluded by default."""
        movies = [
            PlexMovie(rating_key="1", title="Released Movie", tmdb_id=100),
        ]
        plex = self._create_mock_plex_client(movies)

        movie_collections = {100: 1}
        collections = {
            1: TMDBCollection(
                id=1,
                name="Test Collection",
                parts=[
                    TMDBMovie(id=100, title="Released Movie", release_date=date(2020, 1, 1)),
                    TMDBMovie(id=101, title="Future Movie", release_date=date(2099, 12, 31)),
                ],
            ),
        }
        tmdb = self._create_mock_tmdb_client(movie_collections, collections)

        finder = MovieGapFinder(plex, tmdb, include_future=False)
        report = finder.find_gaps()

        # Collection should be complete (future movie excluded)
        assert report.collections_with_gaps == []

    def test_find_gaps_includes_future_when_enabled(self) -> None:
        """Test that future releases are included when flag is set."""
        movies = [
            PlexMovie(rating_key="1", title="Released Movie", tmdb_id=100),
        ]
        plex = self._create_mock_plex_client(movies)

        movie_collections = {100: 1}
        collections = {
            1: TMDBCollection(
                id=1,
                name="Test Collection",
                parts=[
                    TMDBMovie(id=100, title="Released Movie", release_date=date(2020, 1, 1)),
                    TMDBMovie(id=101, title="Future Movie", release_date=date(2099, 12, 31)),
                ],
            ),
        }
        tmdb = self._create_mock_tmdb_client(movie_collections, collections)

        finder = MovieGapFinder(plex, tmdb, include_future=True)
        report = finder.find_gaps()

        assert len(report.collections_with_gaps) == 1
        gap = report.collections_with_gaps[0]
        assert gap.missing_count == 1
        assert gap.missing_movies[0].title == "Future Movie"

    def test_find_gaps_progress_callback(self) -> None:
        """Test that progress callback is called."""
        movies = [
            PlexMovie(rating_key="1", title="Movie 1", tmdb_id=100),
        ]
        plex = self._create_mock_plex_client(movies)
        tmdb = self._create_mock_tmdb_client({100: None}, {})

        progress_calls = []

        def progress_callback(stage: str, current: int, total: int) -> None:
            progress_calls.append((stage, current, total))

        finder = MovieGapFinder(plex, tmdb, progress_callback=progress_callback)
        finder.find_gaps()

        # Should have progress updates
        assert len(progress_calls) > 0
        stages = {call[0] for call in progress_calls}
        assert "Fetching movies from Plex" in stages
        assert "Checking collection membership" in stages

    def test_find_gaps_movies_without_tmdb_id_skipped(self) -> None:
        """Test that movies without TMDB IDs are counted but skipped."""
        movies = [
            PlexMovie(rating_key="1", title="With ID", tmdb_id=100),
            PlexMovie(rating_key="2", title="Without ID"),  # No TMDB ID
        ]
        plex = self._create_mock_plex_client(movies)
        tmdb = self._create_mock_tmdb_client({100: None}, {})

        finder = MovieGapFinder(plex, tmdb)
        report = finder.find_gaps()

        assert report.total_movies_scanned == 2
        assert report.movies_with_tmdb_id == 1
