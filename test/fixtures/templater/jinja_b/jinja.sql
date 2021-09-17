SELECT
    {% for key, value in (("a", 3), ("b", 7)) %}{{ some_func(value) }} as {{ key }}{% if not loop.last %},{% endif %}{% endfor %}
FROM some_table
