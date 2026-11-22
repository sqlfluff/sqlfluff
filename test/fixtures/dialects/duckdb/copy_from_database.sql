-- Copy the schema and data of one database to another
COPY FROM DATABASE db1 TO db2;

-- Copy only the schema
COPY FROM DATABASE db1 TO db2 (SCHEMA);

-- Copy only the data
COPY FROM DATABASE db1 TO db2 (DATA);

-- Quoted database name
COPY FROM DATABASE "source db" TO db2;
