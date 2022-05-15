"""Generate the airflow builtins macros which are injected in the context.

https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
"""
import datetime as dt
import time as t
import uuid as u
import random as r


# https://github.com/apache/airflow/blob/main/airflow/macros/__init__.py
def ds_add(ds: str, days: int) -> str:
    """Add or subtract days from a YYYY-MM-DD.

    :param ds: anchor date in ``YYYY-MM-DD`` format to add to
    :param days: number of days to add to the ds, you can use negative values
    >>> ds_add('2015-01-01', 5)
    '2015-01-06'
    >>> ds_add('2015-01-06', -5)
    '2015-01-01'
    """
    if not days:
        return str(ds)
    return (
        dt.datetime.strptime(str(ds), "%Y-%m-%d") + dt.timedelta(days=days)
    ).strftime("%Y-%m-%d")


def ds_format(ds: str, input_format: str, output_format: str) -> str:
    """Takes an input string and outputs another string.

    As specified in the output format

    :param ds: input string which contains a date
    :param input_format: input string format. E.g. %Y-%m-%d
    :param output_format: output string format  E.g. %Y-%m-%d
    >>> ds_format('2015-01-01', "%Y-%m-%d", "%m-%d-%y")
    '01-01-15'
    >>> ds_format('1/5/2015', "%m/%d/%Y",  "%Y-%m-%d")
    '2015-01-05'
    """
    return dt.datetime.strptime(str(ds), input_format).strftime(output_format)


datetime = dt.datetime
timedelta = dt.timedelta
time = t
uuid = u
random = r.random
