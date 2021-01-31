WITH
  confusion_matrix AS (
  SELECT
    expected_label,
    commerce,
    digital,
    traditional_services
  FROM
    ML.CONFUSION_MATRIX(MODEL model3,
      (
      SELECT
        *
      FROM
        table1
      WHERE
        training = 0 )))

SELECT
  *,
  commerce pct_commerce
FROM
  confusion_matrix
