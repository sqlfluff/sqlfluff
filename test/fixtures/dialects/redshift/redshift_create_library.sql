create library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
credentials 'aws_iam_role=arn:aws:iam::123456789:role/role_name'
region as 'us-east-1';

create library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
region as 'us-east-1'
credentials 'aws_iam_role=arn:aws:iam::123456789:role/role_name';

create or replace library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
with credentials as 'aws_iam_role=arn:aws:iam::123456789:role/role_name'
region as 'us-east-1';

create or replace library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
credentials as 'aws_access_key_id=<temporary-access-key-id>;aws_secret_access_key=<temporary-secret-access-key>;token=<temporary-token>'
region as 'us-east-1';

create or replace library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
with credentials 'aws_access_key_id=<temporary-access-key-id>;aws_secret_access_key=<temporary-secret-access-key>;token=<temporary-token>'
region as 'us-east-1';

create library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
iam_role 'aws_iam_role=arn:aws:iam::123456789:role/role_name';

create or replace library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
ACCESS_KEY_ID '<access-key-id>'
SECRET_ACCESS_KEY '<secret-access-key>';

create or replace library lib1 language plpythonu
from 's3://s3bucket/lib1.0.3.zip'
ACCESS_KEY_ID '<access-key-id>'
SECRET_ACCESS_KEY '<secret-access-key>'
SESSION_TOKEN '<temporary-token>'
region 'us-east-1';

create library lib1 language plpythonu
from 'https://example.com/packages/lib1.0.3.zip';

create or replace library lib1 language plpythonu
from 'https://example.com/packages/lib1.0.3.zip';
