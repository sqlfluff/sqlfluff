"""Module used to test filters within the jinja template."""

from __future__ import annotations

import datetime


# https://github.com/apache/airflow/blob/main/airflow/templates.py#L50
def ds_filter(value: datetime.date | datetime.time | None) -> str | None:
    """Date filter."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")


SQLFLUFF_JINJA_FILTERS = {"ds": ds_filter}

now = datetime.datetime(
    2006, 1, 2, 3, 4, 5, 0, tzinfo=datetime.timezone(-datetime.timedelta(hours=7))
)
