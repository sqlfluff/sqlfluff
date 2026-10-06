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

CREATE OR ALTER WAREHOUSE my_wh;

create warehouse my_wh
    resource_constraint = 'STANDARD_GEN_1'
    warehouse_size = 'medium'
;

create warehouse my_wh
    resource_constraint = STANDARD_GEN_2
    warehouse_size = 'medium'
    SCALING_POLICY = ECONOMY
    comment = 'comment'
    auto_suspend = 60
;

create warehouse my_adaptive_wh warehouse_type = adaptive;

create or replace warehouse gen2_wh with warehouse_size = 'MEDIUM' generation = '2';

-- Object parameters can follow the TAG clause.
create warehouse tagged_wh
    with warehouse_size = 'XSMALL'
    with tag (cost_center = 'sales')
    max_concurrency_level = 8;
