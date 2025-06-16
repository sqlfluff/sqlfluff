-- Simple node table with a user defined attributes
CREATE TABLE [dbo].[Person] (
   ID INTEGER PRIMARY KEY,
   [name] VARCHAR(100)
) AS NODE;

-- A simple edge table with a user defined attribute
CREATE TABLE friends (
   id INTEGER PRIMARY KEY,
   start_date DATE
) AS EDGE;

-- Create a likes edge table, this table does not have any user defined attributes
CREATE TABLE likes AS EDGE;

-- Create friend edge table with CONSTRAINT, restricts for nodes and it direction
CREATE TABLE dbo.FriendOf(
  CONSTRAINT cnt_Person_FriendOf_Person
    CONNECTION (dbo.Person TO dbo.Person)
) AS EDGE;

-- Create friend edge table with CONSTRAINT,
-- with ON DELETE CASCADE option
CREATE TABLE dbo.FriendOf(
  CONSTRAINT cnt_Person_FriendOf_Person
    CONNECTION (dbo.Person TO dbo.Person) ON DELETE CASCADE
) AS EDGE;
