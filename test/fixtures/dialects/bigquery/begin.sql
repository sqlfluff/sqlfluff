BEGIN
  BEGIN;

  INSERT INTO `my_project.my_dataset.my_table`
  SELECT
    col1,
    col2,
    CASE WHEN col1 > col2 THEN False ELSE True END AS col3,
  FROM `my_project.my_dataset.my_other_table`;

  COMMIT TRANSACTION;
END;

BEGIN
  BEGIN TRANSACTION;

  INSERT INTO `my_project.my_dataset.my_table`
  SELECT
    col1,
    col2,
    CASE WHEN col1 > col2 THEN False ELSE True END AS col3,
  FROM `my_project.my_dataset.my_other_table`;

  COMMIT TRANSACTION;
END;

BEGIN
  BEGIN;

  INSERT INTO `my_project.my_dataset.my_table`
  SELECT
    col1,
    col2,
    CASE WHEN col1 > col2 THEN 1 ELSE 2 END AS col3,
    CASE WHEN x > 5 THEN 5 END; -- case with a statement delimiter after

  COMMIT;
END;

mylabel: BEGIN
    BEGIN;
    INSERT INTO `my_project.my_dataset.my_table`
    SELECT 1;
    COMMIT;
END mylabel;
