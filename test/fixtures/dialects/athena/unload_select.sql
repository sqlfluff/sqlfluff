UNLOAD (SELECT field_1, field_2 FROM my_table)
TO 's3://my_athena_data_location/my_folder/'
WITH (format='CSV', compression='gzip', field_delimiter=',', partitioned_by=ARRAY[field_2]);
