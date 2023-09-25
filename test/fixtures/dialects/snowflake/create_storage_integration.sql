create storage integration s3_int
  type = external_stage
  storage_provider = s3
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = ('s3://mybucket1/path1/', 's3://mybucket2/path2/');

create storage integration s3_int
  type = external_stage
  storage_provider = s3
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = ('s3://mybucket1', 's3://mybucket2/');

create storage integration gcs_int
  type = external_stage
  storage_provider = gcs
  enabled = true
  storage_allowed_locations = ('gcs://mybucket1/path1/', 'gcs://mybucket2/path2/');

create storage integration azure_int
  type = external_stage
  storage_provider = azure
  enabled = true
  azure_tenant_id = '<tenant_id>'
  storage_allowed_locations = ('azure://myaccount.blob.core.windows.net/mycontainer/path1/', 'azure://myaccount.blob.core.windows.net/mycontainer/path2/');

create or replace storage integration s3_int
  type = external_stage
  storage_provider = s3
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = ('*')
  storage_blocked_locations = ('s3://mybucket3/path3/', 's3://mybucket4/path4/');

create or replace storage integration gcs_int
  type = external_stage
  storage_provider = gcs
  enabled = true
  storage_allowed_locations = ('*')
  storage_blocked_locations = ('gcs://mybucket3/path3/', 'gcs://mybucket4/path4/');

create or replace storage integration azure_int
  type = external_stage
  storage_provider = azure
  enabled = false
  azure_tenant_id = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
  storage_allowed_locations = ('*')
  storage_blocked_locations = ('azure://myaccount.blob.core.windows.net/mycontainer/path3/', 'azure://myaccount.blob.core.windows.net/mycontainer/path4/');

create storage integration s3_int
  type = external_stage
  storage_provider = 's3'
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = ('s3://mybucket1', 's3://mybucket2/');

create storage integration gcs_int
  type = external_stage
  storage_provider = 'gcs'
  enabled = true
  storage_allowed_locations = ('gcs://mybucket1/path1/', 'gcs://mybucket2/path2/');

create storage integration azure_int
  type = external_stage
  storage_provider = 'azure'
  enabled = true
  azure_tenant_id = '<tenant_id>'
  storage_allowed_locations = ('azure://myaccount.blob.core.windows.net/mycontainer/path1/', 'azure://myaccount.blob.core.windows.net/mycontainer/path2/');
