"""Centralized error handling for ComPlexionist GUI.

Provides user-friendly error display using shared error utilities.
"""

from __future__ import annotations

import flet as ft

# Import shared error message function
from complexionist.errors import get_friendly_message


def show_error(
    page: ft.Page,
    error: Exception | str,
    *,
    duration: int = 5000,
    show_details: bool = False,
) -> None:
    """Show a user-friendly error message as a snackbar.

    Args:
        page: The Flet page to show the error on.
        error: The error (exception or string).
        duration: How long to show the snackbar in milliseconds.
        show_details: If True, include technical details for debugging.
    """
    if isinstance(error, str):
        message = error
        details = None
    else:
        message = get_friendly_message(error)
        details = str(error) if show_details else None

    # Build snackbar content
    content: ft.Control
    if details and details != message:
        content = ft.Column(
            [
                ft.Text(message),
                ft.Text(details, size=10, color=ft.Colors.GREY_400),
            ],
            spacing=4,
            tight=True,
        )
    else:
        content = ft.Text(message)

    snack = ft.SnackBar(
        content=content,
        bgcolor=ft.Colors.RED_700,
        duration=duration,
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()


def show_warning(
    page: ft.Page,
    message: str,
    *,
    duration: int = 4000,
) -> None:
    """Show a warning message as a snackbar.

    Args:
        page: The Flet page to show the warning on.
        message: The warning message.
        duration: How long to show the snackbar in milliseconds.
    """
    snack = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.ORANGE_700,
        duration=duration,
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()


def show_success(
    page: ft.Page,
    message: str,
    *,
    duration: int = 3000,
) -> None:
    """Show a success message as a snackbar.

    Args:
        page: The Flet page to show the message on.
        message: The success message.
        duration: How long to show the snackbar in milliseconds.
    """
    snack = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.GREEN_700,
        duration=duration,
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()


def show_info(
    page: ft.Page,
    message: str,
    *,
    duration: int = 3000,
) -> None:
    """Show an info message as a snackbar.

    Args:
        page: The Flet page to show the message on.
        message: The info message.
        duration: How long to show the snackbar in milliseconds.
    """
    snack = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.BLUE_700,
        duration=duration,
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()
