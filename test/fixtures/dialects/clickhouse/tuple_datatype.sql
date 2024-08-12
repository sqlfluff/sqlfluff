SELECT (1, 'two', '2024-01-01')::Tuple(id Int64, name String, created_at Date32) as struct;

SELECT (1, 'two', '2024-01-01')::Tuple(`id` Int64, `name` String, `created_at` Date32) as struct;

SELECT (1, 'two', '2024-01-01')::`Tuple(id Int64, name String, created_at Date32)` as struct;
