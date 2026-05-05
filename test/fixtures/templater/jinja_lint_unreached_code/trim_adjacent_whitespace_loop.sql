select
    foo,
    {% for i in range(1, 3) %}
        i as col{{ i }}
        {%- if not loop.last -%}
            ,
        {%- endif -%}
    {% endfor %}
from foo
