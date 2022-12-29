{% if not is_incremental() %}
    SELECT 1
{% else %}
    SELECT c
    FROM t
    WHERE c < 0
{% endif %}
