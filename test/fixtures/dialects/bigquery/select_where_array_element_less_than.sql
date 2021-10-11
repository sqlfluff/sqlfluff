SELECT
  *
FROM
  `project.dataset.table_1`
WHERE
  effect_size_list[ORDINAL(1)] < effect_size_list[ORDINAL(1+1)]
