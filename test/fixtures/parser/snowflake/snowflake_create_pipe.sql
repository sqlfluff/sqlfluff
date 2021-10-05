create or replace pipe mypipe_s3
  auto_ingest = true
  aws_sns_topic = 'arn:aws:blablabla..0:s3_mybucket'
  as
  copy into snowpipe_db.public.mytable
  from @snowpipe_db.public.mystage
  file_format = (type = 'JSON');
