SELECT 1 INTO OUTFILE '/tmp/test';

SELECT 1 as test INTO OUTFILE '/tmp/test' FORMAT TabSeparated;

SELECT test FROM dual where test = '1' INTO OUTFILE '/tmp/test' FORMAT TabSeparated;

SELECT test FROM dual INTO OUTFILE '/tmp/test' FORMAT CSV;
