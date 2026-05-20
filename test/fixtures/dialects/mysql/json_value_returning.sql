SELECT JSON_VALUE('{"a":"b"}', '$.a') AS basic_example;
SELECT JSON_VALUE('{"a":"b"}', '$.a' RETURNING CHAR) AS returning_char;
SELECT JSON_VALUE('{"a":"b"}', '$.a' RETURNING CHAR(255) CHARACTER SET utf8mb4) AS returning_charset;
SELECT JSON_VALUE('{"a":"1"}', '$.a' RETURNING UNSIGNED) AS returning_unsigned;
SELECT JSON_VALUE('{"a":"1"}', '$.a' RETURNING SIGNED) AS returning_signed;