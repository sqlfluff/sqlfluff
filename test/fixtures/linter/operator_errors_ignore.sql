/* This is a file to test the inline ignoring of certain rules.
Errors should be found in line 10, but not on line 9. Line 10 has
rules ignored, but there are rules which *arent* ignored, which
are still present. No errors should be found on line 8 at all. */

SELECT
    a.a + a.b AS good,
    a.a-a.b AS bad_1,  -- noqa
    a.a*a.b AS bad_2,  -- noqa: LT01, LT03
    a.a*a.b AS bad_3  -- noqa: LT03
FROM tbl AS a
