"""ANSI color helpers for terminal output."""

from typing import Optional

# ANSI escape sequences
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"

_ENABLED = True


def disable() -> None:
    """Globally disable color output (e.g., when writing to a file)."""
    global _ENABLED
    _ENABLED = False


def enable() -> None:
    """Re-enable color output."""
    global _ENABLED
    _ENABLED = True


def _wrap(code: str, text: str) -> str:
    if not _ENABLED:
        return text
    return f"{code}{text}{RESET}"


def bold(text: str) -> str:
    return _wrap(BOLD, text)


def dim(text: str) -> str:
    return _wrap(DIM, text)


def red(text: str) -> str:
    return _wrap(FG_RED, text)


def green(text: str) -> str:
    return _wrap(FG_GREEN, text)


def yellow(text: str) -> str:
    return _wrap(FG_YELLOW, text)


def blue(text: str) -> str:
    return _wrap(FG_BLUE, text)


def cyan(text: str) -> str:
    return _wrap(FG_CYAN, text)


def highlight_schedule(text: str) -> str:
    """Apply a consistent highlight style for schedule entries."""
    return green(bold(text))


def highlight_header(text: str) -> str:
    """Apply a consistent style for section headers."""
    return cyan(bold(text))


def highlight_error(text: str) -> str:
    """Apply a consistent style for error messages."""
    return red(bold(text))
