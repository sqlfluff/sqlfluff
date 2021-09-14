-- Copyright (c) 2020 De Staat der Nederlanden, Ministerie van   Volksgezondheid, Welzijn en Sport.
-- Licensed under the EUROPEAN UNION PUBLIC LICENCE v. 1.2 - see https://github.com/minvws/nl-contact-tracing-app-coordinationfor more information.

IF NOT EXISTS(SELECT * FROM sys.indexes WHERE NAME='IX_INTER_RIVM_INFECTIOUS_PEOPLE')
    CREATE NONCLUSTERED INDEX IX_INTER_RIVM_INFECTIOUS_PEOPLE
    ON VWSINTER.RIVM_INFECTIOUS_PEOPLE(DATE_LAST_INSERTED);
GO

IF NOT EXISTS(SELECT * FROM sys.indexes WHERE NAME='IX_INTER_FOUNDATION_NICE_IC_INTAKE_COUNT')
    CREATE NONCLUSTERED INDEX IX_INTER_FOUNDATION_NICE_IC_INTAKE_COUNT
    ON VWSINTER.FOUNDATION_NICE_IC_INTAKE_COUNT(DATE_LAST_INSERTED);
GO

IF NOT EXISTS(SELECT * FROM sys.indexes WHERE NAME='IX_INTER_RIVM_REPRODUCTION_NUMBER')
    CREATE NONCLUSTERED INDEX IX_INTER_RIVM_REPRODUCTION_NUMBER
    ON VWSINTER.RIVM_INFECTIOUS_PEOPLE(DATE_LAST_INSERTED);
GO
