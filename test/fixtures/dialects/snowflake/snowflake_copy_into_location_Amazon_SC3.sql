copy into 's3://mybucket/unload/'
  from mytable
  credentials = (aws_key_id='xxxx' aws_secret_key='xxxxx' aws_token='xxxxxx')
  file_format = (format_name = my_csv_format);
