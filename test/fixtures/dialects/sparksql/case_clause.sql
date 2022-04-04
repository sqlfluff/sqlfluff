SELECT
    id,
    CASE
        WHEN id > 200 THEN 'bigger'
        ELSE 'small'
    END
FROM person;

SELECT
    id,
    CASE
        WHEN id > 200 THEN 'bigger'
        ELSE 'small'
    END AS id_size
FROM person;

SELECT
    id,
    CASE id
        WHEN 100 THEN 'bigger'
        WHEN id > 300 THEN '300'
        ELSE 'small'
    END
FROM person;

SELECT id
FROM person
WHERE
    CASE 1 = 1
        WHEN 100 THEN 'big'
        WHEN 200 THEN 'bigger'
        WHEN 300 THEN 'biggest'
        ELSE 'small'
    END = 'small';
