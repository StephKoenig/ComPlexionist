"""Command-line interface for ComPlexionist."""

import click
from rich.console import Console

from complexionist import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="complexionist")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """ComPlexionist - Find missing movies and TV episodes in your Plex library."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@main.command()
@click.option("--library", "-l", default=None, help="Movie library name (default: auto-detect)")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
@click.option("--include-future", is_flag=True, help="Include unreleased movies")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format",
)
@click.pass_context
def movies(
    ctx: click.Context,
    library: str | None,
    no_cache: bool,
    include_future: bool,
    format: str,
) -> None:
    """Find missing movies from collections in your Plex library."""
    verbose = ctx.obj.get("verbose", False)
    console.print("[yellow]Movie collection gaps feature coming soon![/yellow]")
    if verbose:
        console.print(f"  Library: {library or 'auto-detect'}")
        console.print(f"  Cache: {'disabled' if no_cache else 'enabled'}")
        console.print(f"  Include future: {include_future}")
        console.print(f"  Format: {format}")


@main.command()
@click.option("--library", "-l", default=None, help="TV library name (default: auto-detect)")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
@click.option("--include-future", is_flag=True, help="Include unaired episodes")
@click.option("--include-specials", is_flag=True, help="Include Season 0 (specials)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format",
)
@click.pass_context
def episodes(
    ctx: click.Context,
    library: str | None,
    no_cache: bool,
    include_future: bool,
    include_specials: bool,
    format: str,
) -> None:
    """Find missing episodes from TV shows in your Plex library."""
    verbose = ctx.obj.get("verbose", False)
    console.print("[yellow]TV episode gaps feature coming soon![/yellow]")
    if verbose:
        console.print(f"  Library: {library or 'auto-detect'}")
        console.print(f"  Cache: {'disabled' if no_cache else 'enabled'}")
        console.print(f"  Include future: {include_future}")
        console.print(f"  Include specials: {include_specials}")
        console.print(f"  Format: {format}")


@main.command()
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
@click.option("--include-future", is_flag=True, help="Include unreleased content")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format",
)
@click.pass_context
def scan(
    ctx: click.Context,
    no_cache: bool,
    include_future: bool,
    format: str,
) -> None:
    """Scan both movie and TV libraries for missing content."""
    console.print("[bold blue]ComPlexionist Scan[/bold blue]")
    console.print()

    # Invoke movies command
    console.print("[bold]Movie Collections[/bold]")
    ctx.invoke(movies, no_cache=no_cache, include_future=include_future, format=format)
    console.print()

    # Invoke episodes command
    console.print("[bold]TV Episodes[/bold]")
    ctx.invoke(
        episodes,
        no_cache=no_cache,
        include_future=include_future,
        include_specials=False,
        format=format,
    )


@main.group()
def config() -> None:
    """Manage ComPlexionist configuration."""
    pass


@config.command(name="show")
def config_show() -> None:
    """Show current configuration."""
    console.print("[yellow]Configuration display coming soon![/yellow]")


@config.command(name="path")
def config_path() -> None:
    """Show configuration file paths."""
    from pathlib import Path

    home = Path.home()
    config_dir = home / ".complexionist"

    console.print("[bold]Configuration paths:[/bold]")
    console.print(f"  Config dir:  {config_dir}")
    console.print(f"  Cache dir:   {config_dir / 'cache'}")
    console.print(f"  .env file:   {Path.cwd() / '.env'}")


@main.group()
def cache() -> None:
    """Manage the API response cache."""
    pass


@cache.command(name="clear")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def cache_clear() -> None:
    """Clear all cached API responses."""
    console.print("[yellow]Cache clearing coming soon![/yellow]")


@cache.command(name="stats")
def cache_stats() -> None:
    """Show cache statistics."""
    console.print("[yellow]Cache statistics coming soon![/yellow]")


if __name__ == "__main__":
    main()
