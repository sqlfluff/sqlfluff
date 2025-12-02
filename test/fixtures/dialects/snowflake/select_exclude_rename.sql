select * exclude col1 rename (col1 as alias1, col2 as alias2) from table1;

select * exclude (col1, col2) rename col1 as alias1 from table1;

select * exclude (col1, col2) rename (col1 as alias1, col2 as alias2) from table1;
