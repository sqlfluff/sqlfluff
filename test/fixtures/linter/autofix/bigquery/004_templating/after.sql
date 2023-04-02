
/*
A nice hairy templated query to really stretch and test templating and fixing.

This file should fail the safety checks, and so the position of the templated
tokens shouldn't move.
*/
WITH
raw_effect_sizes AS (
    SELECT
        COUNT(1) AS campaign_count,
        {{corr_states}}
        {% for action in considered_actions %}
            , SAFE_DIVIDE(SAFE_MULTIPLY(CORR({{metric}}_rate_su, {{action}}), STDDEV_POP({{metric}}_rate_su)), STDDEV_POP({{action}})) AS {{metric}}_{{action}}
        {% endfor %}
    FROM
        `{{gcp_project}}.{{dataset}}.global_actions_states`
    GROUP BY
        {{corr_states}}
),

{% for action in considered_actions %}
    {{action}}_raw_effect_sizes AS (
        SELECT
            COUNT(1) AS campaign_count_{{action}},
            {{corr_states}}
            -- NOTE: The LT02 fix routine behaves a little strangely here around the templated
            -- code, specifically the indentation of STDDEV_POP and preceding comments. This
            -- is a bug currently with no obvious solution.
            , SAFE_DIVIDE(
                SAFE_MULTIPLY(CORR({{metric}}_rate_su, {{action}}), STDDEV_POP({{metric}}_rate_su)),
                STDDEV_POP({{action}})
            ) AS {{metric}}_{{action}}
        FROM
            `{{gcp_project}}.{{dataset}}.global_actions_states`
        WHERE
            {{action}} != -1
        GROUP BY
            {{corr_states}}
    ),
{% endfor %}

new_raw_effect_sizes AS (
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
),

imputed_effect_sizes AS (
    SELECT
        {{corr_states}}
        , o.campaign_count AS campaign_count
        {% for action in considered_actions %}
            , COALESCE(IF(IS_NAN(o.{{metric}}_{{action}}), 0, o.{{metric}}_{{action}}), 0) AS {{metric}}_{{action}}
            , COALESCE(IF(IS_NAN(n.{{metric}}_{{action}}), 0, n.{{metric}}_{{action}}), 0) AS new_{{metric}}_{{action}}
            , n.campaign_count_{{action}}
        {% endfor %}
    FROM
        raw_effect_sizes o
    JOIN
        new_raw_effect_sizes n
        USING
            ({{corr_states}})
),

action_states AS (
    SELECT
        {{action_states}}
    FROM `{{gcp_project}}.{{dataset}}.global_state_space`
    GROUP BY {{action_states}})

SELECT
    imputed_effect_sizes.*,
    {{action_states}}
FROM
    imputed_effect_sizes
CROSS JOIN action_states
