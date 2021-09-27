IF NOT EXISTS(SELECT * FROM sys.sequences WHERE object_id = OBJECT_ID(N'[dbo].[SEQ_SCHEMA_NAME_TABLE_NAME]') AND type = 'SO')
CREATE SEQUENCE SEQ_SCHEMA_NAME_TABLE_NAME
  START WITH 1
  INCREMENT BY 1;
GO

CREATE TABLE SCHEMA_NAME.TABLE_NAME(
	[ID] INT PRIMARY KEY NOT NULL DEFAULT (NEXT VALUE FOR [dbo].[SEQ_SCHEMA_NAME_TABLE_NAME]),
	[WEEK_UNIX] BIGINT,
	GMCODE VARCHAR(100),
	AVERAGE_RNA_FLOW_PER_100000 DECIMAL(16,2) NULL,
	NUMBER_OF_MEASUREMENTS INT NULL,
	NUMBER_OF_LOCATIONS INT NULL,
	TOTAL_LOCATIONS INT NULL,
	DATE_LAST_INSERTED DATETIME DEFAULT GETDATE()
);

IF NOT EXISTS(SELECT * FROM sys.sequences WHERE object_id = OBJECT_ID(N'[dbo].[SEQ_STAGE_CBS_POPULATION_BASE]') AND type = 'SO')
CREATE SEQUENCE SEQ_STAGE_CBS_POPULATION_BASE
  START WITH 1
  INCREMENT BY 1;
GO

CREATE TABLE STAGE.CBS_POPULATION_BASE(
	[ID] INT PRIMARY KEY NONCLUSTERED NOT NULL DEFAULT (NEXT VALUE FOR [dbo].[SEQ_STAGE_CBS_POPULATION_BASE]),
  GEMEENTE_CODE  VARCHAR(100) NULL,
  GEMEENTE VARCHAR(100) NULL,
  LEEFTIJD VARCHAR(100) NULL,
  GESLACHT VARCHAR(100) NULL,
  DATUM_PEILING VARCHAR(100) NULL,
  POPULATIE VARCHAR(100) NULL,
  VEILIGHEIDSREGIO_CODE VARCHAR(100) NULL,
  VEILIGHEIDSREGIO_NAAM VARCHAR(100) NULL,
  PROVINCIE_CODE VARCHAR(100) NULL,
  PROVINCIE_NAAM VARCHAR(100) NULL,
  GGD_CODE VARCHAR(100) NULL,
  GGD_NAAM VARCHAR(100) NULL,
	DATE_LAST_INSERTED DATETIME DEFAULT GETDATE()
);
GO
CREATE CLUSTERED INDEX CI_DLI_STAGE_CBS_POPULATION_BASE ON STAGE.CBS_POPULATION_BASE (DATE_LAST_INSERTED)
GO
CREATE NONCLUSTERED INDEX NCI_DLI_STAGE_CIMS_VACCINATED_AGE_GROUP 
ON STAGE.CBS_POPULATION_BASE (DATE_LAST_INSERTED, GEMEENTE_CODE, GEMEENTE, LEEFTIJD, GESLACHT, DATUM_PEILING, POPULATIE, 
VEILIGHEIDSREGIO_CODE, VEILIGHEIDSREGIO_NAAM, PROVINCIE_CODE, PROVINCIE_NAAM, GGD_CODE, GGD_NAAM);


CREATE TABLE DEST.POSITIVE_TESTED_PEOPLE(
	[ID] INT PRIMARY KEY NOT NULL DEFAULT (NEXT VALUE FOR [dbo].[SEQ_DEST_POSITIVE_TESTED_PEOPLE]),
	DATE_OF_REPORT DATETIME NULL,
	DATE_OF_REPORT_UNIX BIGINT NULL,
	INFECTED_DAILY_INCREASE DECIMAL(16, 1) NULL,
	INFECTED_DAILY_TOTAL INT NULL,
	DATE_LAST_INSERTED DATETIME DEFAULT GETDATE(),
    [DATE_RANGE_START] datetime,
	[DATE_OF_REPORTS_LAG] datetime,
	[DATE_RANGE_START_LAG] datetime,
	[7D_AVERAGE_INFECTED_DAILY_INCREASE_TOTAL] decimal (16,2),
    [7D_AVERAGE_INFECTED_DAILY_INCREASE_LAG] decimal (16,2),
	[7D_AVERAGE_INFECTED_DAILY_INCREASE_ABSOLUTE] decimal (16,2)
 );