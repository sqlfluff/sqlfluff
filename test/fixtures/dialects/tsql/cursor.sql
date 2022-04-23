DECLARE @pointy CURSOR LOCAL FORWARD_ONLY READ_ONLY FOR
SELECT column_a, column_b FROM some_table WHERE column_a IS NOT NULL ORDER BY column_b

OPEN @pointy;

CLOSE GLOBAL @pointy;

DEALLOCATE @pointy;
