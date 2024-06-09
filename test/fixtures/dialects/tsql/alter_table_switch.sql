--TRUNCATE_TARGET is Azure Synapse Analytics specific
ALTER TABLE [Facility].[PL_stage] SWITCH TO [Facility].[PL_BASE] WITH (TRUNCATE_TARGET = ON);

-- https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql
ALTER TABLE [PartitionTable] SWITCH PARTITION 1 TO NonPartitionTable;

ALTER TABLE Orders SWITCH PARTITION 2 TO [OrdersHistory] PARTITION 2;

ALTER TABLE Orders SWITCH PARTITION 3 TO [OrdersHistory] PARTITION 3;

ALTER TABLE Orders SWITCH PARTITION 4 TO [OrdersHistory] PARTITION 4 WITH (
    WAIT_AT_LOW_PRIORITY ( MAX_DURATION = 15 MINUTES, ABORT_AFTER_WAIT = NONE )
);

ALTER TABLE Orders SWITCH PARTITION 5 TO [OrdersHistory] PARTITION 5 WITH (
    WAIT_AT_LOW_PRIORITY ( MAX_DURATION = 25, ABORT_AFTER_WAIT = SELF )
);
