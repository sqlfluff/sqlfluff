//// CHANGE name=alter1

ALTER TABLE table1 ADD COLUMN colY NUMBER;

ALTER TABLE table1 ADD COLUMN colZ NUMBER;

//// METADATA test
//// CHANGE name="init"
CREATE TABLE OrigTable (
    Field1 int,
    Field2 int
)
//// CHANGE name="dropOld" DROP_TABLE dependencies="OldToNewTableMigration.migration"
