put file:///tmp/data/mydata.csv @my_int_stage;
put file:///tmp/data/orders_001.csv @%orderstiny_ext auto_compress=false;
put file:///tmp/data/orders_*01.csv @%orderstiny_ext auto_compress=false;
put file://c:\temp\data\mydata.csv @~ auto_compress=true;
put file://c:\temp\data\mydata.csv @~ parallel=1;
put file://c:\temp\data\mydata.csv @~ source_compression='auto_detect';
put file://c:\temp\data\mydata.csv @~ overwrite=true;
