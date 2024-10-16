CREATE VIEW v1 AS SELECT * FROM tbl;
CREATE OR REPLACE VIEW v1 AS SELECT 42;
CREATE VIEW v1(a) AS SELECT 42;
create view if not exists v as select 1;
