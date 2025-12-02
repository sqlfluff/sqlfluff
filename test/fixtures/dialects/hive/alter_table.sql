ALTER TABLE schema.table1 rename TO schema.table2;

ALTER TABLE schema.table1 rename TO schema.table2;

ALTER TABLE table2 EXCHANGE PARTITION (ds='1') WITH TABLE table1;
