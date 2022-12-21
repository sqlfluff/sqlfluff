DECLARE x INT64 DEFAULT 0;

REPEAT
  SET x = x + 1;
  SELECT x;
  UNTIL x >= 3
END REPEAT;

WHILE true DO
  SELECT 1;
  CONTINUE;
END WHILE;

IF x >= 10 THEN
	SELECT x;
END IF;

IF x >= 10 THEN
	SET x = x - 1;
ELSEIF x < 0 THEN
	SET x = x + 1;
ELSEIF x = 0 THEN
	SET x = x + 1;
ELSE
	SELECT x;
END IF;

LOOP
  SET x = x + 1;
  IF x >= 10 THEN
    LEAVE;
  ELSE
	CONTINUE;
  END IF;
END LOOP;
SELECT x;

DECLARE heads BOOL;
DECLARE heads_count INT64 DEFAULT 0;
LOOP
  SET heads = RAND() < 0.5;
  IF heads THEN
    SELECT 'Heads!';
    SET heads_count = heads_count + 1;
    CONTINUE;
  END IF;
  SELECT 'Tails!';
  BREAK;
END LOOP;
SELECT CONCAT(CAST(heads_count AS STRING), ' heads in a row');
