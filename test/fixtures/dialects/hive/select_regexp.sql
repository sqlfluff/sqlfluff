SELECT *
    FROM example
    WHERE url REGEXP '(/click)';

SELECT
        *,
        url REGEXP '(/click)'
    FROM example;

SELECT *
    FROM example
    WHERE url IREGEXP '(/click)';

SELECT
        *,
        url IREGEXP '(/click)'
    FROM example;

SELECT *
    FROM example
    WHERE url RLIKE '(/click)';

SELECT
        *,
        url RLIKE '(/click)'
    FROM example;
