{%- macro group_by(n) -%}

  group by {% for i in range(1, n + 1) -%}
      {{ i }}{{ ',' if not loop.last }}   
   {%- endfor -%}

{%- endmacro -%}
