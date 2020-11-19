-- A subset of the hairy test.
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
