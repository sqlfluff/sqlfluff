{{
	config(materialized='table')
}}

SELECT
    FIRST_COLUMN,
    SECOND_COLUMN
FROM TABLE_TO_TEST
where TYPE_OF_TEST = 'TESTING ÅÄÖ'
