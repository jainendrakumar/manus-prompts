"""Locale-safe numeric parsing utilities."""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ISO 8601 duration pattern: P0DT0H0M6.577S
_ISO_DURATION_RE = re.compile(
    r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:([\d.]+)S)?",
    re.IGNORECASE,
)


def parse_iso_duration(value: str) -> Optional[float]:
    """Parse ISO 8601 duration string to milliseconds.

    Examples:
        P0DT0H0M6.577S -> 6577.0
        P0DT0H1M30.5S  -> 90500.0
    """
    if not value:
        return None
    m = _ISO_DURATION_RE.match(value.strip())
    if not m:
        logger.warning("Cannot parse ISO duration: %s", value)
        return None
    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0)
    minutes = int(m.group(3) or 0)
    seconds = float(m.group(4) or 0)
    total_ms = ((days * 86400) + (hours * 3600) + (minutes * 60) + seconds) * 1000.0
    return total_ms


def parse_number(value: str, context: str = "") -> Tuple[Optional[float], Optional[str]]:
    """Parse a numeric string handling locale ambiguity.

    Handles:
        - 5,321     -> 5321.0 (thousand separator)
        - 1,704     -> 1704.0 (thousand separator)
        - 153352.19 -> 153352.19
        - 5.321     -> 5.321 (decimal)
        - 1.704.123 -> ambiguous

    Returns:
        Tuple of (parsed_value, warning_message_or_None)
    """
    if not value or not value.strip():
        return None, None

    s = value.strip()

    # Handle n/a or non-numeric markers
    if s.lower() in ("n/a", "na", "none", "-", ""):
        return None, None

    warning = None

    # Count separators
    commas = s.count(",")
    dots = s.count(".")

    if commas == 0 and dots <= 1:
        # Simple case: no commas, at most one dot (standard decimal)
        try:
            return float(s), None
        except ValueError:
            return None, f"Cannot parse number: '{s}' ({context})"

    if commas > 0 and dots == 0:
        # Commas only: treat as thousand separators
        # Validate: groups of 3 digits after first comma
        cleaned = s.replace(",", "")
        try:
            result = float(cleaned)
            # Check if comma positions are valid thousand separators
            parts = s.split(",")
            if len(parts[0]) <= 3 and all(len(p) == 3 for p in parts[1:]):
                return result, None
            else:
                warning = f"Ambiguous comma-separated number: '{s}' ({context}), treating as thousand separator"
                return result, warning
        except ValueError:
            return None, f"Cannot parse number: '{s}' ({context})"

    if commas == 0 and dots > 1:
        # Multiple dots: treat as thousand separators (European format)
        cleaned = s.replace(".", "")
        try:
            result = float(cleaned)
            warning = f"Multiple dots in number: '{s}' ({context}), treating as thousand separators"
            return result, warning
        except ValueError:
            return None, f"Cannot parse number: '{s}' ({context})"

    if commas > 0 and dots == 1:
        # Commas and one dot: commas are thousand separators, dot is decimal
        cleaned = s.replace(",", "")
        try:
            return float(cleaned), None
        except ValueError:
            return None, f"Cannot parse number: '{s}' ({context})"

    if commas == 1 and dots == 0:
        # Single comma could be decimal separator (European) or thousand separator
        # Heuristic: if exactly 3 digits after comma, treat as thousand separator
        parts = s.split(",")
        if len(parts[1]) == 3:
            cleaned = s.replace(",", "")
            try:
                result = float(cleaned)
                warning = f"Ambiguous single comma: '{s}' ({context}), treating as thousand separator"
                return result, warning
            except ValueError:
                return None, f"Cannot parse number: '{s}' ({context})"
        else:
            # Treat comma as decimal separator
            cleaned = s.replace(",", ".")
            try:
                return float(cleaned), None
            except ValueError:
                return None, f"Cannot parse number: '{s}' ({context})"

    return None, f"Cannot parse number: '{s}' ({context})"


def safe_float(value: str, context: str = "") -> float:
    """Parse a float value, returning 0.0 on failure and logging warnings."""
    result, warning = parse_number(value, context)
    if warning:
        logger.warning(warning)
    return result if result is not None else 0.0


def safe_int(value: str, default: int = 0) -> int:
    """Parse an integer value safely."""
    if not value:
        return default
    try:
        return int(value.strip().replace(",", ""))
    except (ValueError, TypeError):
        return default
