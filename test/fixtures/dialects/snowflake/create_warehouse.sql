create or replace warehouse my_wh with warehouse_size='X-LARGE';
create or replace warehouse my_wh warehouse_size=large initially_suspended=true;
create warehouse if not exists LOAD_WH warehouse_size='medium';
create warehouse if not exists LOAD_WH warehouse_size='medium' warehouse_type = standard;

create warehouse my_wh
    WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED'
    warehouse_size = 'medium'
    SCALING_POLICY = ECONOMY
    comment = 'comment'
    auto_suspend = 60
;
