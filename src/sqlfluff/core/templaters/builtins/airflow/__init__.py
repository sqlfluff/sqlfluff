"""Generate the airflow builtins which are injected in the context.

https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
"""
import datetime

import sqlfluff.core.templaters.builtins.airflow.filters as filters


class DagEmulator:
    """A class which emulates the `DAG` class from Airflow."""

    dag_id = "sample_dag"
    is_subdag = False

    def __str__(self):
        return self.dag_id


class DagRunEmulator:
    """A class which emulates the `task` class from Airflow."""

    dag_id = "sample_dag"
    run_id = "sample_dag__run_id"
    execution_date = datetime.datetime.now(datetime.timezone.utc)
    logical_date = datetime.datetime.now(datetime.timezone.utc)
    state = "SUCCESS"
    is_backfill = False

    def __str__(self):
        return self.run_id


class TaskInstanceEmulator:
    """A class which emulates the `task_instance` class from Airflow."""

    dag_id = "sample_dag"
    task_id = "sample_task"
    ds_nodash = "19700101"

    logical_date = datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return f"{self.dag_id}__{self.task_id}__{self.ds_nodash}"


data_interval_start = datetime.datetime.now() + datetime.timedelta(days=-1)
data_interval_end = datetime.datetime.now()
ds = filters.ds_filter(DagRunEmulator().logical_date)
ds_nodash = filters.ds_nodash_filter(DagRunEmulator().logical_date)
ts = filters.ts_filter(DagRunEmulator().logical_date)
ts_nodash_with_tz = filters.ts_nodash_with_tz_filter(DagRunEmulator().logical_date)
ts_nodash = filters.ts_nodash_filter(DagRunEmulator().logical_date)
task_instance_key_str = str(TaskInstanceEmulator())
task_instance = TaskInstanceEmulator()
dag = DagEmulator()
ti = TaskInstanceEmulator()
dag_run = DagRunEmulator()

# Deprecated Airflow variables
next_ds = datetime.date.today() + datetime.timedelta(days=1)
prev_ds = datetime.date.today() + datetime.timedelta(days=-1)
