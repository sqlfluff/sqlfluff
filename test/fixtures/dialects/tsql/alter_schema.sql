ALTER SCHEMA HumanResources TRANSFER Person.Address;

ALTER SCHEMA Person TRANSFER type::Production.TestType;

ALTER SCHEMA Sales TRANSFER OBJECT::dbo.Region;

ALTER SCHEMA [Sales] TRANSFER [dbo].[Region];

ALTER SCHEMA Sales TRANSFER OBJECT :: dbo.Region;

ALTER SCHEMA dbo TRANSFER XML SCHEMA COLLECTION::Sales.ManuInstructionsSchemaCollection;

ALTER SCHEMA stage TRANSFER Region;
