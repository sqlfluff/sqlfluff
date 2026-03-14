-- DELETE with OUTPUT as derived table
INSERT INTO tbl1
SELECT id FROM (
    DELETE tbl2
    OUTPUT deleted.id
) AS x;

-- UPDATE with OUTPUT as derived table
SELECT * FROM (
    UPDATE tbl3
    SET col1 = 'value'
    OUTPUT inserted.id, deleted.col1, inserted.col1
) AS updated_data;

-- INSERT with OUTPUT as derived table
SELECT new_id FROM (
    INSERT INTO tbl4 (name)
    OUTPUT inserted.id AS new_id
    VALUES ('test')
) AS ins;

-- DELETE with OUTPUT and WHERE clause
SELECT deleted_id FROM (
    DELETE FROM tbl5
    OUTPUT deleted.id AS deleted_id
    WHERE status = 'inactive'
) AS del_result;

-- Complex DELETE with OUTPUT and JOIN in outer query
SELECT d.id, t.name
FROM (
    DELETE tbl6
    OUTPUT deleted.id, deleted.category_id
    WHERE deleted_date < '2020-01-01'
) AS d
INNER JOIN tbl7 t ON d.category_id = t.id;
