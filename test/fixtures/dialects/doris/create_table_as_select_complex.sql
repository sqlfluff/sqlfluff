CREATE TABLE t10
PROPERTIES (
  'replication_num' = '1',
  'storage_medium' = 'SSD'
)
AS SELECT 
  id,
  name,
  COUNT(*) as count
FROM t1 
WHERE status = 'active'
GROUP BY id, name; 