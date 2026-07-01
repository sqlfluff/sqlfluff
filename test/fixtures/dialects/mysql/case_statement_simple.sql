CREATE PROCEDURE `testprocedure`(IN val int)
BEGIN
  CASE val
    WHEN 1 THEN SELECT 'one';
    WHEN 2 THEN SELECT 'two';
    ELSE SELECT 'other';
  END CASE;
END~
