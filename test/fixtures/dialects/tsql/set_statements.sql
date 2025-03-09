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

-- Assignment operators
SET @param1 += 1,
    @param2 -= 2,
    @param3 *= 3,
    @param4 /= 4,
    @param5 %= 5,
    @param5 ^= 6,
    @param5 &= 7,
    @param5 |= 8
;

-- Param with sequence in expression
SET @param1 = (NEXT VALUE FOR [dbo].[SEQUENCE_NAME])
;

-- Param set to NULL value is treated as assignment not comparison (issue #6000)
SET @param1 = NULL
;
