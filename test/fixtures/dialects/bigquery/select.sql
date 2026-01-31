SELECT 'metadata' AS key from foo;

-- Test Hexadecimal Integer Literal
SELECT 0x01 AS hex1;
SELECT 0xFF AS hex2;
SELECT 0xDEADBEEF AS hex3;
SELECT CASE WHEN TRUE THEN 0x01 ELSE 0x00 END;
SELECT 0x01 | 0x02 AS bitwise_or;

