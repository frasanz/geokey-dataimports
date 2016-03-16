"""All helpers for the type."""

import time

from iso8601 import parse_date
from iso8601.iso8601 import ParseError


def is_numeric(value=''):
    """
    Check if the value is numeric.

    Parameters
    ----------
    value : str
        Value to check.

    Returns
    -------
    boolean
        Whether the value is numeric.
    """
    if isinstance(value, (str, unicode)):
        try:
            float(value) if '.' in value else int(value)
        except ValueError:
            return False

    return True


def is_date(value=''):
    """
    Check if the value is date.

    Parameters
    ----------
    value : str
        Value to check.

    Returns
    -------
    boolean
        Whether the value is date.
    """
    try:
        parse_date(str(value))
    except ParseError:
        return False

    return True


def is_time(value=''):
    """
    Check if the value is time.

    Parameters
    ----------
    value : str
        Value to check.

    Returns
    -------
    boolean
        Whether the value is time.
    """
    try:
        time.strptime(str(value), '%H:%M')
    except ValueError:
        return False

    return True
