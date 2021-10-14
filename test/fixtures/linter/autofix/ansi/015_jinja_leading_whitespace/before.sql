

{%- set x = 42 %}
SELECT 1, 2;


{% set x = 56 -%}
SELECT 3, 4;


{% set x = 42 %}
SELECT 1, 2
