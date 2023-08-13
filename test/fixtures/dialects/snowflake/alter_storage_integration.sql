alter storage integration test_integration set
    tag tag1 = 'value1';

alter storage integration test_integration set
    tag tag1 = 'value1', tag2 = 'value2';

alter storage integration test_integration
    set comment = 'test comment';

alter storage integration test_integration unset
    comment;

alter storage integration test_integration unset
    tag tag1, tag2;

alter storage integration if exists test_integration unset
    tag tag1, tag2;

alter storage integration test_integration unset
     enabled;

alter storage integration test_integration unset
    comment;

alter storage integration test_integration unset
    storage_blocked_locations;

alter storage integration test_integration set
    enabled = true;

alter storage integration test_integration
    set enabled = false
    comment = 'test comment';

alter storage integration test_integration set
    comment = 'test comment'
    enabled = false;

alter storage integration test_integration set
    storage_aws_role_arn = 'test_role_arn';

alter storage integration test_integration set
    storage_aws_object_acl = 'test_object_acl';

alter storage integration test_integration set
    azure_tenant_id = 'test_azure_tenant_id';

alter storage integration s3_int set
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = (
    's3://mybucket1', 's3://mybucket2/'
  );

alter storage integration gcs_int set
  enabled = true
  storage_allowed_locations = (
    'gcs://mybucket1/path1/',
    'gcs://mybucket2/path2/'
  );

alter storage integration azure_int set
  enabled = true
  azure_tenant_id = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
  storage_allowed_locations = (
    'azure://myaccount.blob.core.windows.net/mycontainer/path1/',
    'azure://myaccount.blob.core.windows.net/mycontainer/path2/'
  );

alter storage integration s3_int set
  storage_aws_role_arn = 'arn:aws:iam::001234567890:role/myrole'
  enabled = true
  storage_allowed_locations = ('*')
  storage_blocked_locations = (
    's3://mybucket3/path3/', 's3://mybucket4/path4/'
    );


alter storage integration gcs_int set
  enabled = true
  storage_allowed_locations = ('*')
  storage_blocked_locations = (
    'gcs://mybucket3/path3/', 'gcs://mybucket4/path4/'
    );


alter storage integration azure_int set
  enabled = true
  azure_tenant_id = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
  storage_allowed_locations = ('*')
  storage_blocked_locations = (
    'azure://myaccount.blob.core.windows.net/mycontainer/path3/',
    'azure://myaccount.blob.core.windows.net/mycontainer/path4/'
    );

alter storage integration azure_int set
  enabled = true
  comment = 'test_comment'
  azure_tenant_id = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
  storage_allowed_locations = ('*')
  storage_blocked_locations = (
    'azure://myaccount.blob.core.windows.net/mycontainer/path3/',
    'azure://myaccount.blob.core.windows.net/mycontainer/path4/'
    );

alter storage integration if exists azure_int set
  enabled = true
  comment = 'test_comment'
  azure_tenant_id = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
  storage_allowed_locations = ('*')
  storage_blocked_locations = (
    'azure://myaccount.blob.core.windows.net/mycontainer/path3/',
    'azure://myaccount.blob.core.windows.net/mycontainer/path4/'
    );
