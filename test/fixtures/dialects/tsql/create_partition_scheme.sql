-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-partition-function-transact-sql#BKMK_examples

CREATE PARTITION SCHEME myRangePS1
AS PARTITION myRangePF1
TO (test1fg, test2fg, test3fg, test4fg);


CREATE PARTITION SCHEME myRangePS3
AS PARTITION myRangePF3
ALL TO ( test1fg );

CREATE PARTITION SCHEME myRangePS1
AS PARTITION myRangePF1
ALL TO ( [PRIMARY] );
