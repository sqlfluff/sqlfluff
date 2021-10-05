CREATE TABLE users (
    username TEXT,
    age INT CHECK(age > 18)
);

CREATE TABLE users (
    username TEXT,
    age INT CHECK(age IS NOT NULL)
);

CREATE TABLE Persons (
    ID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Age int,
    City varchar(255),
    CONSTRAINT CHK_Person CHECK (Age>=18 AND City='Sandnes')
);
