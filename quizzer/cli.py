"""
CLI utilities for Quizzer command-line tools.

Shared helpers used by both run_quiz.py and import_quiz.py:
  - ASCII art logo
  - ANSI color output (with NO_COLOR / --no-color support)
  - Progress bar and score bar rendering

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

import os
import sys

# ---------------------------------------------------------------------------
# Color support detection
# ---------------------------------------------------------------------------

def _color_enabled() -> bool:
    """
    Return True if ANSI color output should be used.

    Respects the NO_COLOR env var (https://no-color.org/) and detects
    non-TTY output (pipes, redirects) automatically.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


_USE_COLOR: bool = _color_enabled()


def disable_color() -> None:
    """Disable ANSI color output (call after parsing --no-color flag)."""
    global _USE_COLOR
    _USE_COLOR = False


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

class _C:
    """ANSI escape code constants."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    WHITE  = "\033[97m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_RED   = "\033[91m"


def _c(code: str, text: str) -> str:
    """Wrap text in ANSI code if color is enabled."""
    if not _USE_COLOR:
        return text
    return f"{code}{text}{_C.RESET}"


def green(text: str) -> str:
    """Return text in bright green (used for correct answers, success)."""
    return _c(_C.BRIGHT_GREEN, text)


def red(text: str) -> str:
    """Return text in bright red (used for incorrect answers, errors)."""
    return _c(_C.BRIGHT_RED, text)


def yellow(text: str) -> str:
    """Return text in yellow (used for warnings, prompts)."""
    return _c(_C.YELLOW, text)


def cyan(text: str) -> str:
    """Return text in cyan (used for info, headers)."""
    return _c(_C.CYAN, text)


def bold(text: str) -> str:
    """Return text in bold."""
    return _c(_C.BOLD, text)


def dim(text: str) -> str:
    """Return text dimmed (used for secondary info)."""
    return _c(_C.DIM, text)


# ---------------------------------------------------------------------------
# ASCII art logo
# ---------------------------------------------------------------------------

_LOGO_LINES = [
    r"  ___  _   _ ___ __________ _____ ____  ",
    r" / _ \| | | |_ _|__  /__  /|_  _||  _ \ ",
    r"| | | | | | || |  / /  / /   | |  | |_) |",
    r"| |_| | |_| || | / /_ / /_  _| |_ |  _ < ",
    " \\__\\_\\\\___/|___/____|____|_|_____|_| \\_\\",
]

_TAGLINE = "CLI Quiz Runner  |  v1.0"

# Border auto-sized to widest logo line + 2 padding chars each side
_INNER_WIDTH = max(len(ln) for ln in _LOGO_LINES) + 4
_BORDER_WIDTH = _INNER_WIDTH + 2   # +2 for the | chars


def print_logo(tagline: bool = True) -> None:
    """
    Print the Quizzer ASCII art logo to stdout.

    Args:
        tagline: Whether to print the tagline below the logo (default: True)
    """
    border = cyan("+" + "-" * _INNER_WIDTH + "+")
    print()
    print(border)
    for line in _LOGO_LINES:
        padded = ("  " + line).ljust(_INNER_WIDTH)
        print(cyan("|") + bold(cyan(padded)) + cyan("|"))
    if tagline:
        tl = _TAGLINE.center(_INNER_WIDTH)
        print(cyan("|") + dim(tl) + cyan("|"))
    print(border)
    print()


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

_BAR_FILL   = "\u2588"   # █
_BAR_EMPTY  = "\u2591"   # ░
_BAR_WIDTH  = 20


def progress_bar(current: int, total: int, width: int = _BAR_WIDTH) -> str:
    """
    Build a text progress bar string.

    Args:
        current: Questions answered so far (0-based ok)
        total:   Total number of questions
        width:   Bar character width (default 20)

    Returns:
        Formatted string, e.g.  [████████░░░░░░░░░░░░]  4/10

    Example:
        >>> bar = progress_bar(4, 10)
        >>> assert "4/10" in bar
    """
    if total <= 0:
        ratio = 0.0
    else:
        ratio = min(current / total, 1.0)

    filled = round(ratio * width)
    empty  = width - filled

    bar_body = (_BAR_FILL * filled) + (_BAR_EMPTY * empty)

    if _USE_COLOR:
        bar_str = (
            _C.CYAN + "[" + _C.RESET
            + _C.GREEN + (_BAR_FILL * filled) + _C.RESET
            + _C.DIM + (_BAR_EMPTY * empty) + _C.RESET
            + _C.CYAN + "]" + _C.RESET
        )
    else:
        bar_str = f"[{bar_body}]"

    label = bold(f"  {current}/{total}")
    return f"{bar_str}{label}"


# ---------------------------------------------------------------------------
# Score bar (results display)
# ---------------------------------------------------------------------------

def score_bar(
    percentage: float,
    pass_threshold: float = 80.0,
    width: int = _BAR_WIDTH,
) -> str:
    """
    Build a visual score bar with pass/fail colouring.

    Args:
        percentage:     Score as float 0-100
        pass_threshold: Minimum % to pass (default 80.0)
        width:          Bar character width (default 20)

    Returns:
        Formatted string e.g.  [████████████████░░░░]  80.0%  PASS

    Example:
        >>> bar = score_bar(84.0)
        >>> assert "PASS" in bar
        >>> bar = score_bar(55.0)
        >>> assert "FAIL" in bar
    """
    ratio  = min(percentage / 100.0, 1.0)
    filled = round(ratio * width)
    empty  = width - filled
    passed = percentage >= pass_threshold

    bar_body = (_BAR_FILL * filled) + (_BAR_EMPTY * empty)
    result_text = "PASS" if passed else "FAIL"

    if _USE_COLOR:
        color_code = _C.BRIGHT_GREEN if passed else _C.BRIGHT_RED
        bar_str = (
            _C.CYAN + "[" + _C.RESET
            + color_code + (_BAR_FILL * filled) + _C.RESET
            + _C.DIM + (_BAR_EMPTY * empty) + _C.RESET
            + _C.CYAN + "]" + _C.RESET
        )
        result_str = _c(color_code + _C.BOLD, f" {percentage:.1f}%  {result_text}")
    else:
        bar_str = f"[{bar_body}]"
        result_str = f" {percentage:.1f}%  {result_text}"

    return f"{bar_str}{result_str}"


# ---------------------------------------------------------------------------
# Section dividers
# ---------------------------------------------------------------------------

def divider(width: int = _BORDER_WIDTH, char: str = "-") -> str:
    """Return a styled horizontal divider line."""
    return dim(char * width)


def section(title: str, width: int = _BORDER_WIDTH) -> str:
    """Return a styled section header line."""
    line = f"  {title}  ".center(width, "-")
    return cyan(line)
