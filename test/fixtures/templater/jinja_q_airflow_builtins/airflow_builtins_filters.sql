SELECT
    '{{ dag_run.logical_date | ds }}',
    '{{ dag_run.logical_date | ds_nodash }}',
    '{{ dag_run.logical_date | ts }}',
    '{{ dag_run.logical_date | ts_nodash }}',
    '{{ dag_run.logical_date | ts_nodash_with_tz }}'
