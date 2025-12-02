SELECT {{ is_incremental() }}
FROM t_table1
{% if is_incremental() %}
WHERE TRUE
{% endif %}
