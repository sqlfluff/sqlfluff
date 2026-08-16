CREATE DATA METRIC FUNCTION governance.dmfs.count_positive_numbers (
    arg_t TABLE (arg_c1 NUMBER, arg_c2 NUMBER)
)
RETURNS NUMBER
AS
'SELECT COUNT_IF(arg_c1 > 0 AND arg_c2 > 0) FROM arg_t';

CREATE OR REPLACE DATA METRIC FUNCTION IF NOT EXISTS governance.dmfs.freshness_hours (
    arg_t TABLE (arg_c1 TIMESTAMP_LTZ)
)
RETURNS NUMBER NOT NULL
COMMENT = 'Hours since the most recent update'
AS
$$
    SELECT TIMEDIFF(hour, MAX(arg_c1), SNOWFLAKE.CORE.DATA_METRIC_SCHEDULED_TIME()) FROM arg_t
$$;

-- DMFs are identified by their TABLE( ... ) signature in ALTER and DROP.
ALTER FUNCTION governance.dmfs.count_positive_numbers(TABLE(NUMBER, NUMBER)) SET COMMENT = 'counts positive rows';

DROP FUNCTION governance.dmfs.freshness_hours(TABLE(TIMESTAMP_LTZ));
