create or replace external table ext_table
     with location = @mystage/path1/
     file_format = (type = json)
     aws_sns_topic = 'arn:aws:sns:us-west-2:001234567890:s3_mybucket';

create or replace external table "_p08"
    with location=@carpe_datastore_commercial/p08
    auto_refresh=true file_format = (type=parquet)
    pattern='.*[.]parquet.*';
