"""Generate the airflow builtins which are injected in the context.

https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
"""
import datetime

import sqlfluff.core.templaters.jinja_builtins.airflow.filters as filters


class DagEmulator:
    """A class which emulates the `DAG` class from Airflow."""

    dag_id = "sample_dag"
    is_subdag = False

    def __str__(self):
        return self.dag_id


class TaskEmulator:
    """A class which emulates the `Task` class from Airflow."""

    task_id = "sample_task"

    def __str__(self):
        return self.task_id


class DagRunEmulator:
    """A class which emulates the `task` class from Airflow."""

    dag_id = "sample_dag"
    run_id = "sample_dag__run_id"
    logical_date = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
        days=-1
    )
    execution_date = logical_date
    data_interval_start = logical_date
    data_interval_end = logical_date + datetime.timedelta(days=1)
    state = "SUCCESS"
    is_backfill = False

    def __str__(self):
        return self.run_id


class TaskInstanceEmulator:
    """A class which emulates the `task_instance` class from Airflow."""

    dag_id = "sample_dag"
    task_id = "sample_task"
    ds_nodash = "19700101"

    logical_date = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
        days=-1
    )

    def __str__(self):
        return f"{self.dag_id}__{self.task_id}__{self.ds_nodash}"

    # TODO: Find a way to make this work.
    # Maybe let users provide a task_id --> return value mapping somehow
    # def xcom_pull(task_ids, key):
    #     return "An XCom value"


# Trying to make all variables fro this list
# https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html#variables
# available as Jinja templates in SQLFluff
# With the exception of
# - `macros`: macros are loaded from submodule
# - `params`, `var`, `conn`: These are highly dependant on user environment and should
#    be specified by the user via .sqlfluff config or a custom module if needed.
data_interval_start = DagRunEmulator().data_interval_start
data_interval_end = DagRunEmulator().data_interval_end
ds = filters.ds(DagRunEmulator().logical_date)
ds_nodash = filters.ds_nodash(DagRunEmulator().logical_date)
ts = filters.ts(DagRunEmulator().logical_date)
ts_nodash_with_tz = filters.ts_nodash_with_tz(DagRunEmulator().logical_date)
ts_nodash = filters.ts_nodash(DagRunEmulator().logical_date)
prev_data_interval_start_success = (
    DagRunEmulator().data_interval_start + datetime.timedelta(days=-1)
)
prev_data_interval_end_success = (
    DagRunEmulator().data_interval_end + datetime.timedelta(days=-1)
)
prev_start_date_success = DagRunEmulator().logical_date + datetime.timedelta(days=-1)
dag = DagEmulator()
task = TaskEmulator()
task_instance = TaskInstanceEmulator()
ti = TaskInstanceEmulator()
task_instance_key_str = str(TaskInstanceEmulator())
conf = "TBD"
run_id = DagRunEmulator().run_id
dag_run = DagRunEmulator()
test_mode = False

# Deprecated Airflow variables
execution_date = DagRunEmulator().data_interval_start
next_execution_date = DagRunEmulator().data_interval_end
next_ds = filters.ds(next_execution_date)
next_ds_nodash = filters.ds_nodash(next_execution_date)
prev_execution_date = DagRunEmulator().data_interval_start + datetime.timedelta(days=-1)
prev_ds = filters.ds(prev_execution_date)
prev_ds_nodash = filters.ds_nodash(prev_execution_date)
yesterday_ds = filters.ds(execution_date + datetime.timedelta(days=-1))
yesterday_ds_nodash = filters.ds_nodash(execution_date + datetime.timedelta(days=-1))
tomorrow_ds = filters.ds(execution_date + datetime.timedelta(days=1))
tomorrow_ds_nodash = filters.ds_nodash(execution_date + datetime.timedelta(days=1))
prev_execution_date_success = execution_date + datetime.timedelta(days=-1)
