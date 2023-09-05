create or replace external table ext_table
     with location = @mystage/path1/
     file_format = (type = json)
     aws_sns_topic = 'arn:aws:sns:us-west-2:001234567890:s3_mybucket';

create or replace external table "_p08"
    with location=@carpe_datastore_commercial/p08
    auto_refresh=true file_format = (type=parquet)
    pattern='.*[.]parquet.*';

CREATE EXTERNAL TABLE EXTERNAL_TABLES.TRIPS(
  tripduration integer as try_cast(VALUE:c1::varchar as integer) not null,
  starttime timestamp as try_cast(VALUE:c2::varchar as timestamp),
  stoptime timestamp as try_cast(VALUE:c3::varchar as timestamp),
  start_station_id integer as try_cast(VALUE:c4::varchar as integer) null,
  start_station_name varchar as (VALUE:c5::varchar),
  start_station_latitude float as try_cast(VALUE:c6::varchar as float),
  start_station_longitude float as try_cast(VALUE:c7::varchar as float),
  end_station_id integer as try_cast(VALUE:c8::varchar as integer),
  end_station_name varchar as (VALUE:c9::varchar),
  end_station_latitude float as try_cast(VALUE:c10::varchar as float),
  end_station_longitude float as try_cast(VALUE:c11::varchar as float),
  bikeid integer as try_cast(VALUE:c12::varchar as integer),
  membership_type varchar as (VALUE:c13::varchar),
  usertype varchar as (VALUE:c14::varchar),
  birth_year integer as try_cast(VALUE:c15::varchar as integer),
  gender integer as try_cast(VALUE:c16::varchar as integer),
  year integer as (substr(metadata$filename, 22, 4)::integer)
)
 PARTITION BY (year)
 LOCATION = @external_tables.citibike_trips
 FILE_FORMAT = ( TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' );
