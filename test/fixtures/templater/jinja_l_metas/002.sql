SELECT
    {{ "      c2\n" }} AS other_id,
    {{ states }}
    {% for action in actions %}
        , {{metric}}_{{action}}
        , campaign_count_{{action}}
    {% endfor %}
FROM
    {% for action in actions %}
        {% if loop.first %}
            {{action}}_raw_effect_sizes
        {% else %}
        JOIN
            {{action}}_raw_effect_sizes
        USING
            ({{ states }})
        {% endif %}
    {% endfor %}
CROSS JOIN action_states
