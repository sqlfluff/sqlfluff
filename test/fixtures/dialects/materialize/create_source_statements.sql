
CREATE SOURCE avro_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'test_topic')
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  WITH (SIZE = '3xsmall');

CREATE VIEW jsonified_kafka_source AS
  SELECT
    data->>'field1' AS field_1,
    data->>'field2' AS field_2,
    data->>'field3' AS field_3
  FROM (SELECT CONVERT_FROM(data, 'utf8')::jsonb AS data FROM json_source);

CREATE SOURCE proto_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'test_topic')
  FORMAT PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  WITH (SIZE = '3xsmall');

CREATE SOURCE text_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'test_topic')
  FORMAT TEXT
  ENVELOPE UPSERT
  WITH (SIZE = '3xsmall');

CREATE SOURCE csv_source (col_foo, col_bar, col_baz)
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'test_topic')
  FORMAT CSV WITH 3 COLUMNS
  WITH (SIZE = '3xsmall');

CREATE SOURCE auction_house
  FROM LOAD GENERATOR AUCTION
  FOR ALL TABLES
  WITH (SIZE = '3xsmall');

CREATE SOURCE tpch
  FROM LOAD GENERATOR TPCH (SCALE FACTOR 1)
  FOR ALL TABLES
  WITH (SIZE = '3xsmall');

CREATE SOURCE counter
  FROM LOAD GENERATOR COUNTER
  WITH (SIZE = '3xsmall');

CREATE SOURCE mz_source
    FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
    FOR ALL TABLES
    WITH (SIZE = '3xsmall');

CREATE SOURCE mz_source
  FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
  FOR TABLES (table_1, table_2 AS alias_table_2)
  WITH (SIZE = '3xsmall');

CREATE SOURCE mz_source
  FROM POSTGRES CONNECTION pg_connection (
    PUBLICATION 'mz_source',
    TEXT COLUMNS (table.column_of_unsupported_type)
  ) FOR ALL TABLES
  WITH (SIZE = '3xsmall');

CREATE SOURCE mz_source
  FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
  WITH (SIZE = '3xsmall');

CREATE TYPE type_name AS ( field_name field_type , field_name field_type );

CREATE TYPE row_type AS (a int, b text);

CREATE TYPE nested_row_type AS (a row_type, b float8);
