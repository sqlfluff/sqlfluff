SELECT col1
FROM t_table1
{% if is_incremental() is true %}
--This is should not be part of the rendered SQL!
WHERE FALSE
{% endif %}
