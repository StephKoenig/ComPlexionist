"""First-run setup wizard for ComPlexionist."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

from complexionist.config import find_config_file, save_default_config

console = Console()


def detect_first_run() -> bool:
    """Check if this is a first-run (no config exists).

    Returns:
        True if no config file was found, False otherwise.
    """
    return find_config_file() is None


def run_setup_wizard() -> Path | None:
    """Run the interactive setup wizard.

    Guides the user through setting up:
    - Plex URL and token
    - TMDB API key
    - TVDB API key (optional)

    Returns:
        Path to created config file, or None if cancelled.
    """
    console.print()
    console.print("[bold blue]ComPlexionist Setup Wizard[/bold blue]")
    console.print()
    console.print("Let's set up your configuration. You'll need:")
    console.print("  1. Your Plex server URL and token")
    console.print("  2. A TMDB API key (for movies)")
    console.print("  3. A TVDB API key (optional, for TV shows)")
    console.print()

    if not Confirm.ask("Ready to continue?", default=True):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return None

    console.print()

    # Plex configuration
    console.print("[bold]Plex Server[/bold]")
    console.print(
        "[dim]Find your Plex token at: "
        "https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/[/dim]"
    )

    plex_url = Prompt.ask(
        "Plex server URL",
        default="http://localhost:32400",
    )
    plex_token = Prompt.ask(
        "Plex token (X-Plex-Token)",
        password=True,
    )
    console.print()

    # TMDB configuration
    console.print("[bold]TMDB API Key[/bold]")
    console.print(
        "[dim]Get your API key at: https://www.themoviedb.org/settings/api[/dim]"
    )
    tmdb_api_key = Prompt.ask("TMDB API key", password=True)
    console.print()

    # TVDB configuration
    console.print("[bold]TVDB API Key (Optional)[/bold]")
    console.print(
        "[dim]Get your API key at: https://thetvdb.com/api-information[/dim]"
    )
    console.print("[dim]Required only for TV show gap detection.[/dim]")
    tvdb_api_key = Prompt.ask("TVDB API key (press Enter to skip)", default="", password=True)
    console.print()

    # Choose config location
    console.print("[bold]Configuration Location[/bold]")
    config_path = Path.cwd() / "complexionist.cfg"
    console.print(f"Config will be saved to: [cyan]{config_path}[/cyan]")

    if not Confirm.ask("Save configuration?", default=True):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return None

    # Save the config
    save_default_config(
        path=config_path,
        plex_url=plex_url,
        plex_token=plex_token,
        tmdb_api_key=tmdb_api_key,
        tvdb_api_key=tvdb_api_key,
    )

    console.print()
    console.print(f"[green]Configuration saved to:[/green] {config_path}")
    console.print()

    # Offer to validate
    if Confirm.ask("Would you like to validate the configuration?", default=True):
        from complexionist.validation import validate_config

        console.print()
        validate_config()

    return config_path


def check_first_run() -> bool:
    """Check for first run and offer to run setup wizard.

    Returns:
        True if setup was completed or config already exists, False if cancelled.
    """
    if not detect_first_run():
        return True

    console.print()
    console.print("[yellow]No configuration file found.[/yellow]")
    console.print()

    if Confirm.ask("Would you like to run the setup wizard?", default=True):
        result = run_setup_wizard()
        return result is not None

    console.print()
    console.print("[dim]You can run 'complexionist config init' later to create a config file.[/dim]")
    console.print()
    return False
