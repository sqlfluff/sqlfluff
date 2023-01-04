{%- set vals = "has_used_small_subject_line\n ,has_used_personal_subject\n ,has_used_personal_to\n" -%}
WITH action_states AS (
  SELECT {{vals}}
  FROM foo
  GROUP BY {{vals}})

SELECT {{vals}}
FROM vals
