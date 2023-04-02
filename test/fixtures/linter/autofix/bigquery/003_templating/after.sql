-- A subset of the hairy test.
-- NOTE: This is not perfect, but reflects
-- functionality as at Nov 2020. In future
-- the logic should be updated to lint this
-- better.

-- Force indentation linting.
-- sqlfluff: indentation: template_blocks_indent: force

SELECT
    {{corr_states}}
    {% for action in considered_actions %}
        , {{metric}}_{{action}}
        , campaign_count_{{action}}
    {% endfor %}
FROM
{% for action in considered_actions %}
    {% if loop.first %}
        {{action}}_raw_effect_sizes
    {% else %}
    JOIN
        {{action}}_raw_effect_sizes
        USING
            ({{corr_states}})
    {% endif %}
{% endfor %}
CROSS JOIN action_states
