-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-partition-scheme-transact-sql#examples

CREATE PARTITION FUNCTION myIntRangePF1 (INT)
AS RANGE LEFT FOR VALUES (1, 100, 1000);

CREATE PARTITION FUNCTION myIntRangePF2 (CHAR(1))
AS RANGE RIGHT FOR VALUES ('A', 'B', 'C');

CREATE PARTITION FUNCTION [myDateRangePF1] (date)
AS RANGE RIGHT FOR VALUES (
    '20030201', '20030301', '20030401',
    '20030501', '20030601', '20030701', '20030801',
    '20030901', '20031001', '20031101', '20031201'
);
