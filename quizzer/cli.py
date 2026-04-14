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
# ASCII art logo  —  ANSI Shadow style, QUIZZER, 6 rows × 55 chars
# 2-D diagonal gradient: bright white (top-left highlight) → deep blue
# (bottom-right shadow), giving a 3-D lit-from-top-left appearance.
# E has 3 horizontal bars — clearly not an I
# ---------------------------------------------------------------------------

_LOGO_ROWS = [
    " ██████╗ ██╗   ██╗██╗███████╗ ███████╗ ███████╗██████╗ ",
    "██╔═══██╗██║   ██║██║╚════██║ ╚════██║ ██╔════╝██╔══██╗",
    "██║   ██║██║   ██║██║    ██╔╝     ██╔╝ █████╗  ██████╔╝",
    "██║▄▄ ██║██║   ██║██║   ██╔╝     ██╔╝  ██╔══╝  ██╔══██╗",
    "╚██████╔╝╚██████╔╝██║ ███████╗ ███████╗███████╗██║  ██║",
    " ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚══════╝ ╚══════╝╚══════╝╚═╝  ╚═╝",
]

# 2-D colour table: _LOGO_2D[row][col_segment]
# 3 column segments per row; colour shifts both down and to the right.
#
#          col-left         col-mid          col-right
_LOGO_2D = [
    ["\033[1;97m",  "\033[1;97m",  "\033[1;96m"],  # row 0 — bold white  → bold cyan
    ["\033[1;97m",  "\033[1;96m",  "\033[96m"  ],  # row 1
    ["\033[1;96m",  "\033[96m",    "\033[1;36m"],  # row 2
    ["\033[96m",    "\033[1;36m",  "\033[36m"  ],  # row 3
    ["\033[1;36m",  "\033[36m",    "\033[34m"  ],  # row 4
    ["\033[36m",    "\033[34m",    "\033[2;34m"],   # row 5 — cyan → deep blue
]

# Column split point: each row is split into thirds
_COL_SPLIT = len(_LOGO_ROWS[0]) // 3   # ≈ 18 chars

# Width used by divider() / section() helpers — matches logo width
_DIVIDER_WIDTH = max(len(r) for r in _LOGO_ROWS)


def print_logo() -> None:
    """
    Print the Quizzer ASCII art logo (ANSI Shadow, 3-D diagonal colour gradient).

    Each row is split into 3 horizontal segments; colour shifts both
    top→bottom and left→right, creating a lit-from-top-left 3-D effect.
    Colour is skipped automatically when output is not a TTY or NO_COLOR is set.
    """
    print()
    for i, row in enumerate(_LOGO_ROWS):
        if not _USE_COLOR:
            print(row)
            continue
        s0 = row[:_COL_SPLIT]
        s1 = row[_COL_SPLIT:2 * _COL_SPLIT]
        s2 = row[2 * _COL_SPLIT:]
        c = _LOGO_2D[i]
        print(c[0] + s0 + _C.RESET + c[1] + s1 + _C.RESET + c[2] + s2 + _C.RESET)
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

def divider(width: int = _DIVIDER_WIDTH, char: str = "-") -> str:
    """Return a styled horizontal divider line."""
    return dim(char * width)


def section(title: str, width: int = _DIVIDER_WIDTH) -> str:
    """Return a styled section header line."""
    line = f"  {title}  ".center(width, "-")
    return cyan(line)
