copy into 'azure://myaccount.blob.core.windows.net/mycontainer/unload/'
  from mytable
  credentials=(azure_sas_token='xxxx')
  file_format = (format_name = my_csv_format);
