copy into mytable
from @my_int_stage;

copy into mytable
from @my_int_stage
file_format = (type = csv);

copy into mytable from @my_int_stage
file_format = (format_name = 'mycsv');

copy into mytable
from @my_int_stage
  file_format = (type = 'CSV')
  pattern='.*/.*/.*[.]csv[.]gz';

copy into mytable
from @my_int_stage
  file_format = (format_name = myformat)
  pattern='.*sales.*[.]csv';

copy into mytable;

copy into mytable purge = true;

copy into mytable validation_mode = 'RETURN_ERRORS';

copy into mytable validation_mode = 'RETURN_2_ROWS';

copy into mytable validation_mode = 'RETURN_3_ROWS';
