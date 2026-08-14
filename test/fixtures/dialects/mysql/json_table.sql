-- Single-table select: COLUMNS definitions must not be read as column
-- references (https://github.com/sqlfluff/sqlfluff/issues/6945).
SELECT
    `jt`.`name`,
    `jt`.`color`,
    `jt`.`price`
FROM JSON_TABLE(
    @json,
    '$[*]'
    COLUMNS(
        `name` VARCHAR(10) PATH '$.name',
        `color` VARCHAR(10) PATH '$.color',
        `price` DECIMAL(8, 2) PATH '$.price'
    )
) AS `jt`;

-- Joined select: the COLUMNS definitions must not trigger qualification rules.
SELECT
    `jt`.`name`,
    `sub`.`size`
FROM (
    SELECT `items`.`size`
    FROM `items`
) AS `sub`
CROSS JOIN JSON_TABLE(
    @json,
    '$[*]'
    COLUMNS(`name` VARCHAR(50) PATH '$.name')
) AS `jt`;

-- FOR ORDINALITY, EXISTS PATH, ON EMPTY / ON ERROR, and NESTED PATH.
SELECT
    `jt`.`id`,
    `jt`.`name`,
    `jt`.`has_price`,
    `jt`.`tag`
FROM JSON_TABLE(
    @json,
    '$[*]'
    COLUMNS(
        `id` FOR ORDINALITY,
        `name` VARCHAR(40) PATH '$.name' DEFAULT '0' ON EMPTY NULL ON ERROR,
        `has_price` VARCHAR(10) EXISTS PATH '$.price',
        NESTED PATH '$.tags[*]' COLUMNS(
            `tag` VARCHAR(40) PATH '$.tag'
        )
    )
) AS `jt`;
