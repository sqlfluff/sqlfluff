INSERT OVERWRITE country_page_view
SELECT
    user_id,
    cnt
FROM page_view_source;

INSERT INTO country_page_view PARTITION (`date` = '2019-08-30', country = 'China')
SELECT
    user_id,
    cnt
FROM page_view_source;

INSERT OVERWRITE country_page_view PARTITION (`date` = '2019-08-30') (user_id, cnt)
SELECT
    user_id,
    cnt
FROM page_view_source;

EXECUTE INSERT INTO country_page_view PARTITION (`date` = '2019-08-30', country = 'China')
SELECT
    user_id,
    cnt
FROM page_view_source;

INSERT INTO target_table
SELECT
    a.id,
    b.val
FROM source_a AS a
INNER JOIN source_b AS b ON a.id = b.id
ON CONFLICT DO DEDUPLICATE;

INSERT INTO target_table
VALUES (1, 'a'), (2, 'b')
ON CONFLICT DO NOTHING;

INSERT INTO target_table
SELECT *
FROM source_table
ON CONFLICT DO ERROR;
