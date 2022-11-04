CREATE EXTERNAL FUNCTION exfunc_sum(INT,INT)
RETURNS INT
STABLE
LAMBDA 'lambda_sum'
IAM_ROLE 'arn:aws:iam::123456789012:role/Redshift-Exfunc-Test';

CREATE OR REPLACE EXTERNAL FUNCTION exfunc_upper()
RETURNS varchar
STABLE
LAMBDA 'exfunc_sleep_3'
IAM_ROLE 'arn:aws:iam::123456789012:role/Redshift-Exfunc-Test'
RETRY_TIMEOUT 0;

CREATE OR REPLACE EXTERNAL FUNCTION exfunc_foo(varchar)
RETURNS int
IMMUTABLE
SAGEMAKER 'some_endpoint_name'
IAM_ROLE default;
