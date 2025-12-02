copy into @%t1
  from t1
  partition by ('date=' || to_varchar(dt, 'YYYY-MM-DD') || '/hour=' || to_varchar(date_part(hour, ts))) -- Concatenate labels and column values to output meaningful filenames
  file_format = (type=parquet)
  max_file_size = 32000000
  header=true;
