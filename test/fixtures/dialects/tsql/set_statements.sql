SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Single params
SET @param1 = 1
;

-- Multiple params
SET @param1 = 1,
    @param2 = 2
;

-- Comma separated params with comment with comma
SET @param1 = "test, test",
    @param2 = 2
;

-- Params with expression
SET @param1 = ("test", "test"),
    @param2 = 2
;
