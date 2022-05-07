# https://github.com/apache/airflow/blob/main/airflow/templates.py
def ds_filter(value):
    return value.strftime("%Y-%m-%d")


def ds_nodash_filter(value):
    return value.strftime("%Y%m%d")


def ts_filter(value):
    return value.isoformat()


def ts_nodash_filter(value):
    return value.strftime("%Y%m%dT%H%M%S")


def ts_nodash_with_tz_filter(value):
    return value.isoformat().replace("-", "").replace(":", "")


airflow_filters = {
    "ds": ds_filter,
    "ds_nodash": ds_nodash_filter,
    "ts": ts_filter,
    "ts_nodash": ts_nodash_filter,
    "ts_nodash_with_tz": ts_nodash_with_tz_filter,
}
