-- A subset of the hairy test.
SELECT
  COUNT(1) AS campaign_count,
  {{corr_states}}
  {% for action in considered_actions %}
  ,aaa(bbb(ccc({{metric}}_r, {{action}}), ddd({{metric}}_r)), eee({{action}})) AS {{metric}}_{{action}}
  {% endfor %}
FROM
  `{{gcp}}.{{dst}}.gas`
GROUP BY
  {{corr_states}}
