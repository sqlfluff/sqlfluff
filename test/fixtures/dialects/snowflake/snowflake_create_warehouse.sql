create or replace warehouse my_wh with warehouse_size='X-LARGE';
create or replace warehouse my_wh warehouse_size=large initially_suspended=true;
create warehouse if not exists LOAD_WH warehouse_size='medium';
