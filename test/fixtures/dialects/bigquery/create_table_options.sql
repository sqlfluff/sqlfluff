CREATE TABLE table_1
OPTIONS(
    expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
);

CREATE TABLE table_1
OPTIONS(
    expiration_timestamp = TIMESTAMP("2023-01-01 00:00:00 UTC")
);

CREATE TABLE table_1
OPTIONS(
    description = "Test mixed options",
    expiration_timestamp = TIMESTAMP("2023-01-01 00:00:00 UTC")
);
