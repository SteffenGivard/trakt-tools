import re

_UNITS = {
    'y': 365 * 86400,
    'yr': 365 * 86400, 'yrs': 365 * 86400,
    'year': 365 * 86400, 'years': 365 * 86400,
    'mo': 30 * 86400,
    'month': 30 * 86400, 'months': 30 * 86400,
    'w': 7 * 86400,
    'week': 7 * 86400, 'weeks': 7 * 86400,
    'd': 86400,
    'day': 86400, 'days': 86400,
    'h': 3600,
    'hr': 3600, 'hrs': 3600,
    'hour': 3600, 'hours': 3600,
    'm': 60,
    'min': 60, 'mins': 60,
    'minute': 60, 'minutes': 60,
    's': 1,
    'sec': 1, 'secs': 1,
    'second': 1, 'seconds': 1,
}

_PATTERN = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*([a-z]+)\s*$', re.IGNORECASE)


def parse_duration(value):
    """Parse a duration string into seconds.

    Accepts:
      - A plain integer or float string (treated as seconds, for backwards compatibility)
      - A number followed by a unit: 30s, 10m, 2h, 1d (and longer forms like 10min, 2hours)

    Returns the duration in seconds as a float, or None if the value is invalid.
    """
    value = str(value).strip()

    # Plain number — treat as seconds (backwards compat)
    try:
        return float(value)
    except ValueError:
        pass

    m = _PATTERN.match(value)
    if m:
        amount, unit = float(m.group(1)), m.group(2).lower()
        if unit in _UNITS:
            return amount * _UNITS[unit]

    return None
