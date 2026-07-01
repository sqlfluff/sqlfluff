CREATE PROCEDURE `testprocedure`(IN val int)
BEGIN
  CASE
    WHEN val = 1 THEN SELECT 'one';
    WHEN val = 2 THEN SELECT 'two';
  END CASE;
END~
