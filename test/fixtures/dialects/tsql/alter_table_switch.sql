--TRUNCATE_TARGET is Azure Synapse Analytics specific
ALTER TABLE [Facility].[PL_stage] SWITCH TO [Facility].[PL_BASE] WITH (TRUNCATE_TARGET = ON);
