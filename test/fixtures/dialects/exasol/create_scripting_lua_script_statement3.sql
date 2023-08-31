CREATE SCRIPT insert_low_high (param1, param2, param3) AS
    import('function_lib') -- accessing external function
    lowest, highest = function_lib.min_max(param1, param2, param3)
    query([[INSERT INTO t VALUES (:x, :y)]], {x=lowest, y=highest})
/
