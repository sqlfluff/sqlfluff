"""Tests the python routines within LT04."""

import sqlfluff


def test__rules__std_LT04_unparseable():
    """Verify that LT04 doesn't try to fix queries with parse errors.

    This has been observed to frequently cause syntax errors, especially in
    combination with Jinja templating, e.g. undefined template variables.
    """
    # This example comes almost directly from a real-world example. The user
    # accidentally ran "sqlfluff fix" without defining
    # "readability_features_numeric" and "readability_features_count_list", and
    # doing so corrupted their query.
    sql = """
        SELECT
          user_id,
          campaign_id,
          business_type,
          SPLIT(intents, ",") AS intent_list,
          {% for feature in readability_features_numeric %}
            CAST(JSON_EXTRACT(readability_scores,
            '$.data.{{feature}}') AS float64) AS {{feature}} {% if not loop.last %} ,
            {% endif %}
          {% endfor %},
          {% for feature in readability_features_count_list %}
            CAST(JSON_EXTRACT(asset_structure,
            '$.{{feature}}') AS float64) AS {{feature}}_count {% if not loop.last %} ,
            {% endif %}
          {% endfor %},
            track_clicks_text,
            track_clicks_html
        FROM
          t
    """
    result = sqlfluff.lint(sql)
    assert "LT04" not in [r["code"] for r in result]
