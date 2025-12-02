create external schema spectrum_schema
from data catalog
database 'sampledb'
region 'us-west-2'
iam_role 'arn:aws:iam::123456789012:role/MySpectrumRole';

create external schema spectrum_schema
from data catalog
database 'spectrum_db'
iam_role 'arn:aws:iam::123456789012:role/MySpectrumRole'
create external database if not exists;

create external schema hive_schema
from hive metastore
database 'hive_db'
uri '172.10.10.10' port 99
iam_role 'arn:aws:iam::123456789012:role/MySpectrumRole';

create external schema spectrum_schema
from data catalog
database 'spectrum_db'
iam_role 'arn:aws:iam::123456789012:role/myRedshiftRole,arn:aws:iam::123456789012:role/myS3Role'
catalog_role 'arn:aws:iam::123456789012:role/myAthenaRole'
create external database if not exists;

CREATE EXTERNAL SCHEMA IF NOT EXISTS myRedshiftSchema
FROM POSTGRES
DATABASE 'my_aurora_db' SCHEMA 'my_aurora_schema'
URI 'endpoint to aurora hostname' PORT 5432
IAM_ROLE 'arn:aws:iam::123456789012:role/MyAuroraRole'
SECRET_ARN 'arn:aws:secretsmanager:us-east-2:123456789012:secret:development/MyTestDatabase-AbCdEf';

CREATE EXTERNAL SCHEMA sales_schema FROM REDSHIFT DATABASE 'sales_db' SCHEMA 'public';

CREATE EXTERNAL SCHEMA IF NOT EXISTS myRedshiftSchema
FROM MYSQL
DATABASE 'my_aurora_db'
URI 'endpoint to aurora hostname'
IAM_ROLE 'arn:aws:iam::123456789012:role/MyAuroraRole'
SECRET_ARN 'arn:aws:secretsmanager:us-east-2:123456789012:secret:development/MyTestDatabase-AbCdEf';

create external schema spectrum_schema
from data catalog
database 'sampledb'
region 'us-west-2'
iam_role 'arn:aws:iam::123456789012:role/MySpectrumRole';

create external schema my_schema
from kafka
iam_role 'arn:aws:iam::012345678901:role/my_role'
authentication iam
uri 'b-1.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9098,b-2.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9098';

create external schema my_schema
from kafka
authentication none
uri 'b-1.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9092,b-2.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9092';

create external schema my_schema
from kafka
iam_role 'arn:aws:iam::012345678901:role/my_role'
authentication mtls
uri 'lkc-2v531.domz6wj0p.us-west-1.aws.confluent.cloud:9092'
authentication_arn 'arn:aws:acm:region:444455556666:certificate/certificate_ID';

create external schema my_schema
from kafka
iam_role 'arn:aws:iam::012345678901:role/my_role'
authentication mtls
uri 'b-1.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9094,b-2.myTestCluster.123z8u.c2.kafka.us-west-1.amazonaws.com:9094'
secret_arn 'arn:aws:secretsmanager:us-east-1:012345678910:secret:myMTLSSecret';
