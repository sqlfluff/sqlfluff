-- Setting tags according to https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-set-tag

SET TAG ON CATALOG catalog `tag1`=`value1`;
SET TAG ON COLUMN catalog.schema.table.column `tag1`=`value1`;
SET TAG ON SCHEMA catalog.schema tag1=`value1`;
SET TAG ON DATABASE catalog.database `tag1`=value1;
SET TAG ON TABLE catalog.schema.table tag1=value1;
SET TAG ON VIEW catalog.schema.view `tag1`=`value1`;
SET TAG ON VOLUME volume `tag1`=`value1`;

UNSET TAG ON CATALOG catalog `tag1`;
UNSET TAG ON COLUMN catalog.schema.table.column `tag1`;
UNSET TAG ON SCHEMA catalog.schema `tag1`;
UNSET TAG ON DATABASE catalog.database `tag1`;
UNSET TAG ON TABLE catalog.schema.table `tag1`;
UNSET TAG ON VIEW catalog.schema.view `tag1`;
UNSET TAG ON VOLUME volume `tag1`;
