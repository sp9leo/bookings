"""Formatting helpers shared by the API and doctype controllers."""

_SL_WEEKDAYS = [
    "ponedeljek",
    "torek",
    "sreda",
    "četrtek",
    "petek",
    "sobota",
    "nedelja",
]
_SL_MONTHS = [
    "januar",
    "februar",
    "marec",
    "april",
    "maj",
    "junij",
    "julij",
    "avgust",
    "september",
    "oktober",
    "november",
    "december",
]


def format_slovenian_date(dt):
    """Return a datetime as e.g. 'petek, 6. november 2026'."""
    return "{}, {}. {} {}".format(
        _SL_WEEKDAYS[dt.weekday()], dt.day, _SL_MONTHS[dt.month - 1], dt.year
    )
