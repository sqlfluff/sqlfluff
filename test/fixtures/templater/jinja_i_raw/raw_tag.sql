SELECT
    col1,
    {% raw %}
    col2,
    '{{ a_tag_which_should_be_treated_as_raw }}' as col3
    {% endraw %}
FROM my_table
