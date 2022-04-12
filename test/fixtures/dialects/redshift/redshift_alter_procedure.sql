ALTER PROCEDURE first_quarter_revenue(volume INOUT bigint, at_price IN numeric, result OUT int)
RENAME TO quarterly_revenue;

ALTER PROCEDURE first_quarter_revenue(bigint, numeric) RENAME TO quarterly_revenue;

ALTER PROCEDURE quarterly_revenue(volume bigint, at_price numeric) OWNER TO etl_user;
