/* Examples from https://duckdb.org/docs/sql/query_syntax/qualify */

-- Filter based on a WINDOW function defined in the QUALIFY clause
SELECT
    schema_name,
    function_name,
    -- In this example the function_rank column in the select clause is for reference
    row_number()
        OVER (PARTITION BY schema_name ORDER BY function_name)
    AS function_rank
FROM duckdb_functions
QUALIFY
    row_number() OVER (PARTITION BY schema_name ORDER BY function_name) < 3;

-- Filter based on a WINDOW function defined in the SELECT clause
SELECT
    schema_name,
    function_name,
    row_number()
        OVER (PARTITION BY schema_name ORDER BY function_name)
    AS function_rank
FROM duckdb_functions()
QUALIFY
    function_rank < 3;

-- Filter based on a WINDOW function defined in the QUALIFY clause, but using the WINDOW clause
SELECT
    schema_name,
    function_name,
    -- In this example the function_rank column in the select clause is for reference
    row_number() OVER my_window AS function_rank
FROM duckdb_functions()
WINDOW
    my_window AS (PARTITION BY schema_name ORDER BY function_name)
QUALIFY
    row_number() OVER my_window < 3;

-- Filter based on a WINDOW function defined in the SELECT clause, but using the WINDOW clause
SELECT
    schema_name,
    function_name,
    row_number() OVER my_window AS function_rank
FROM duckdb_functions()
WINDOW
    my_window AS (PARTITION BY schema_name ORDER BY function_name)
QUALIFY
    function_rank < 3;
