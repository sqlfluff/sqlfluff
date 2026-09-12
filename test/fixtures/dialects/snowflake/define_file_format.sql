DEFINE FILE FORMAT my_db.my_schema.my_json_format
  TYPE = 'JSON'
  COMPRESSION = NONE
  COMMENT = 'uncompressed JSON file format for raw ingestion';

DEFINE FILE FORMAT my_db.my_schema.my_csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1;
