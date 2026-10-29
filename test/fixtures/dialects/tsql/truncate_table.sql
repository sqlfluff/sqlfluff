TRUNCATE TABLE dbo.SalesOrder;

TRUNCATE TABLE AdventureWorks2022.HumanResources.JobCandidate;

TRUNCATE TABLE PartitionTable1 WITH (PARTITIONS (2));

TRUNCATE TABLE PartitionTable1 WITH (PARTITIONS (2, 4, 6 TO 8));
