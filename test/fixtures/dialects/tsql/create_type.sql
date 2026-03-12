CREATE TYPE person AS TABLE (
    name nvarchar(10),
    height int,
    favorite_color int
);

CREATE TYPE weird_int FROM int;

CREATE TYPE [dbo].[ExampleType] FROM VARCHAR(50);

CREATE TYPE [dbo].[DecimalType] FROM DECIMAL(38, 10);

CREATE TYPE [dbo].[NonNullType] FROM VARCHAR(100) NOT NULL;
