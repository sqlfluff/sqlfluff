-- Not missing space before ON
SELECT * FROM "my_table2"
INNER JOIN "my_database"."my_schema"."my_table"ON ("my_table2".foo = "my_table".foo)
