CREATE SEARCH INDEX my_index
ON example_dataset.example_table(ALL COLUMNS);

CREATE SEARCH INDEX IF NOT EXISTS my_index
ON example_dataset.example_table(x, y, z)
OPTIONS (analyzer = 'NO_OP_ANALYZER');

CREATE VECTOR INDEX my_index
ON example_dataset.example_table(example_column)
STORING(stored_column1, stored_column2)
OPTIONS(index_type = 'IVF');

CREATE OR REPLACE VECTOR INDEX IF NOT EXISTS my_index
ON example_dataset.example_table(x, y, z)
OPTIONS(index_type = 'IVF', distance_type = 'COSINE');
