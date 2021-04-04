-- Example from https://github.com/sqlfluff/sqlfluff/pull/737
SELECT
    {% raw %}
    lower(note_text) NOT LIKE '%daycare: {%'
    AND lower(note_text) NOT LIKE '%grade/ school name:  {%'
    AND lower(note_text) NOT LIKE '%social history:  {%'
    {% endraw %}
    AS foo
FROM my_table
