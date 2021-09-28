SELECT
    job_id
{% for var in top_words %}
    , MAX(CASE WHEN word = '{{var}}' THEN 1 ELSE 0 END) AS {{var}}_word
{% endfor %}
{% for position in range(NUM_EMBEDDING_COMPONENTS) %}
    , safe_cast(vector_array[ORDINAL({{position}})] AS FLOAT64) AS v{{position}}
{% endfor %}
FROM
     tbl
LIMIT 1
