-- JSON_TABLE COLUMNS definitions must not be read as column references
-- (https://github.com/sqlfluff/sqlfluff/issues/6945).
SELECT
    `jt`.`name`,
    `jt`.`price`
FROM JSON_TABLE(
    @json,
    '$[*]'
    COLUMNS(
        `name` VARCHAR(10) PATH '$.name',
        `price` DECIMAL(8, 2) PATH '$.price'
    )
) AS `jt`;
