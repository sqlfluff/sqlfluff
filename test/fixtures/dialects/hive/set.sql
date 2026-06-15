set;
set -v;
set foo = 2;
set foo = 'bar';
set hivevar:cat="Chloe";
set mapreduce.reduce.memory.mb=12000;

set hive.execution.engine=tez;
set tez.runtime.enable.final-merge.in.output=false;
set mapreduce.map.java.opts=-Xmx13107m;
set hivevar:schema = schema_test;
set hivevar:tbl = tbl_test;
set datafilter = 2021 AND 2022;
set list = (1, 2, 3);

SELECT *
FROM ${hivevar:schema}.${hivevar:tbl}
WHERE year BETWEEN ${datafilter}
    AND col1 IN ${list}
;
