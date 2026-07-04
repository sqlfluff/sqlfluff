UPSERT INTO target_table SELECT id, name FROM source_table;

UPSERT INTO target_table (id, name) VALUES (1, 'abc');
