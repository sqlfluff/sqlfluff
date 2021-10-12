select '1'::int::boolean as bool;

update table_name
set
    col1 = CURRENT_TIMESTAMP::TIMESTAMP_TZ,
    col2 = '1'::int::boolean
;
