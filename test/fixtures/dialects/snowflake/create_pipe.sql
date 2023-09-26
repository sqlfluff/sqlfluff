create or replace pipe mypipe_s3
  auto_ingest = true
  error_integration = my_error
  aws_sns_topic = 'arn:aws:blablabla..0:s3_mybucket'
  as
  copy into snowpipe_db.public.mytable
  from @snowpipe_db.public.mystage
  file_format = (type = 'JSON');

create or replace pipe test_pipe
  auto_ingest = true
  integration = notification_integration
  as
  copy into table_name (
    column1,
    column2
  )
  from (select
    $1,
    current_timestamp() as column2
  from @stage_name/folder);

create or replace pipe test_pipe
  auto_ingest = true
  integration = 'notification_integration'
  as
  copy into table_name (
    column1,
    column2
  )
  from (select
    $1,
    current_timestamp() as column2
  from @stage_name/folder);
