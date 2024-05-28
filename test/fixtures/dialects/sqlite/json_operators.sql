SELECT value FROM '[11,22,33,44]' -> 3 WHERE '{"x": "y"}' ->> '$.x' = 'y';


SELECT value FROM '{"a":2,"c":[4,5,{"f":7}]}' -> 'c' WHERE Upper('{"x": "y"}') ->> '$.x' = 'y';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> '$';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> '$.c';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> 'c';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> '$.c[2]';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> '$.c[2].f';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' ->> '$.c[2].f';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> 'c' -> 2 ->> 'f';
SELECT '{"a":2,"c":[4,5],"f":7}' -> '$.c[#-1]';
SELECT '{"a":2,"c":[4,5,{"f":7}]}' -> '$.x';
SELECT '[11,22,33,44]' -> 3;
SELECT '[11,22,33,44]' ->> 3;
SELECT '{"a":"xyz"}' -> '$.a';
SELECT '{"a":"xyz"}' ->> '$.a';
SELECT '{"a":null}' -> '$.a';
SELECT '{"a":null}' ->> '$.a';
