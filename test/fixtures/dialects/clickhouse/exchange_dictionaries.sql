EXCHANGE DICTIONARIES a AND b;
EXCHANGE DICTIONARIES default.a AND default.b;
EXCHANGE DICTIONARIES a AND b ON CLUSTER test;
EXCHANGE DICTIONARIES default.a AND default.b ON CLUSTER test;
-- EXCHANGE DICTIONARIES supports mutiple dictionary pairs
-- https://fiddle.clickhouse.com/739c85b0-2f18-4d14-a396-a41ce568d6d9
EXCHANGE DICTIONARIES a AND b, c AND d;
EXCHANGE DICTIONARIES default.a AND default.b, default.c AND default.d;
EXCHANGE DICTIONARIES a AND b, c AND d ON CLUSTER test;
EXCHANGE DICTIONARIES default.a AND default.b, default.c AND default.d ON CLUSTER test;
