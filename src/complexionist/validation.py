"""Configuration validation for ComPlexionist."""

from __future__ import annotations

from rich.console import Console

from complexionist.config import get_config

console = Console()


def validate_config() -> bool:
    """Validate the current configuration.

    Tests connectivity to:
    - Plex server
    - TMDB API
    - TVDB API (if configured)

    Returns:
        True if all configured services are valid, False otherwise.
    """
    from complexionist.plex import PlexClient, PlexError
    from complexionist.tmdb import TMDBClient, TMDBError
    from complexionist.tvdb import TVDBClient, TVDBError

    console.print("[bold]Validating Configuration[/bold]")
    console.print()

    cfg = get_config()
    all_valid = True

    # Test Plex
    console.print("Plex Server... ", end="")
    if not cfg.plex.url or not cfg.plex.token:
        console.print("[yellow]Not configured[/yellow]")
        all_valid = False
    else:
        try:
            plex = PlexClient()
            plex.connect()
            server_name = plex.server_name if hasattr(plex, "server_name") else "Connected"

            # List libraries
            movie_libs = plex.get_movie_libraries()
            tv_libs = plex.get_tv_libraries()

            console.print(f"[green]OK[/green] ({server_name})")
            if movie_libs:
                console.print(f"  Movie libraries: {', '.join(lib.title for lib in movie_libs)}")
            if tv_libs:
                console.print(f"  TV libraries: {', '.join(lib.title for lib in tv_libs)}")
        except PlexError as e:
            console.print(f"[red]Failed[/red] - {e}")
            all_valid = False

    # Test TMDB
    console.print("TMDB API... ", end="")
    if not cfg.tmdb.api_key:
        console.print("[yellow]Not configured[/yellow]")
        all_valid = False
    else:
        try:
            tmdb = TMDBClient()
            tmdb.test_connection()
            console.print("[green]OK[/green]")
        except TMDBError as e:
            console.print(f"[red]Failed[/red] - {e}")
            all_valid = False

    # Test TVDB
    console.print("TVDB API... ", end="")
    if not cfg.tvdb.api_key:
        console.print("[yellow]Not configured[/yellow] (TV show gaps won't be detected)")
    else:
        try:
            tvdb = TVDBClient()
            tvdb.login()
            console.print("[green]OK[/green]")
        except TVDBError as e:
            console.print(f"[red]Failed[/red] - {e}")
            all_valid = False

    console.print()
    if all_valid:
        console.print("[green]Configuration is valid![/green]")
    else:
        console.print("[yellow]Some services are not configured or failed validation.[/yellow]")

    return all_valid


def validate_plex_only() -> bool:
    """Validate only Plex connectivity.

    Returns:
        True if Plex is configured and accessible, False otherwise.
    """
    from complexionist.plex import PlexClient, PlexError

    cfg = get_config()
    if not cfg.plex.url or not cfg.plex.token:
        return False

    try:
        plex = PlexClient()
        plex.connect()
        return True
    except PlexError:
        return False
