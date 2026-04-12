"""Utility functions for mini_agent CLI."""


def calculate_display_width(text: str) -> int:
    """Calculate display width of text, accounting for ANSI codes.

    Args:
        text: Text that may contain ANSI color codes

    Returns:
        Display width ignoring ANSI codes
    """
    # Remove ANSI escape codes for width calculation
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    clean_text = ansi_escape.sub('', text)
    return len(clean_text)
