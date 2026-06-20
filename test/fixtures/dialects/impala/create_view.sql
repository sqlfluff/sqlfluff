CREATE VIEW IF NOT EXISTS db.my_view (col1 COMMENT 'c1', col2)
  COMMENT 'view comment'
  TBLPROPERTIES ('key1'='val1')
AS SELECT col1, col2 FROM db.src;
