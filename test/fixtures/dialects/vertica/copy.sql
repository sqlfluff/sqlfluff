-- https://docs.vertica.com/latest/en/sql-reference/statements/copy/examples/
-- Some functionality isn't covered yet, so I commented it
COPY public.customer_dimension (
    customer_since FORMAT 'YYYY'
)
   FROM STDIN
   DELIMITER ','
   NULL AS 'null'
   ENCLOSED BY '"';

COPY sampletab FROM '/home/dbadmin/one.dat', 'home/dbadmin/two.dat';

COPY myTable FROM 'webhdfs:///mydirectory/ofmanyfiles/*.dat';

COPY myTable FROM 'webhdfs:///mydirectory/*_[0-9]';

COPY myTable FROM 'webhdfs:///data/sales/01/*.dat', 'webhdfs:///data/sales/02/*.dat',
    'webhdfs:///data/sales/historical.dat';

COPY t FROM 'webhdfs:///opt/data/file1.dat';

COPY t FROM 'webhdfs://testNS/opt/data/file2.csv';

COPY t FROM 's3://AWS_DataLake/*' ORC;

COPY names (
    first,
    middle FILLER VARCHAR(20),
    last
--     , full AS first||' '||middle||' '||last
)
FROM STDIN;
