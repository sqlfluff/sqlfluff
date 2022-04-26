CREATE TYPE my_type AS (
    int_ INT4,
    bool_ BOOLEAN,
    comment_ TEXT
);

SELECT ((1, true, null)::my_type).int_;
