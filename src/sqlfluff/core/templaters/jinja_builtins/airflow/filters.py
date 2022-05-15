"""Generate the airflow builtins filters which are injected in the context.

https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
"""


# https://github.com/apache/airflow/blob/main/airflow/templates.py
def ds(value):
    """Airflow builtin filter ds."""
    return value.strftime("%Y-%m-%d")


def ds_nodash(value):
    """Airflow builtin filter ds_nodash."""
    return value.strftime("%Y%m%d")


def ts(value):
    """Airflow builtin filter ts."""
    return value.isoformat()


def ts_nodash(value):
    """Airflow builtin filter ts_nodash."""
    return value.strftime("%Y%m%dT%H%M%S")


def ts_nodash_with_tz(value):
    """Airflow builtin filter ts_nodash_with_tz."""
    return value.isoformat().replace("-", "").replace(":", "")


def generate_jinja_filters():
    """Returns Airflow Jinja filters."""
    return {
        "ds": ds,
        "ds_nodash": ds_nodash,
        "ts": ts,
        "ts_nodash": ts_nodash,
        "ts_nodash_with_tz": ts_nodash_with_tz,
    }
