create table if not exists "p08_base" as
select
	VALUE:id::TEXT id
from "_p08";

CREATE TABLE IF NOT EXISTS table_name (
   col1 VARCHAR
);

create table mytable (amount number);

create table mytable (amount number) CLUSTER BY (amount);

create table mytable (amount number) CLUSTER BY LINEAR(amount);

create table mytable CLUSTER BY (amount) (amount number);

create table mytable CLUSTER BY LINEAR(amount) (amount number);

create table mytable_copy2 as select b+1 as c from mytable_copy;

create table mytable_2 like mytable;

create temporary table demo_temporary (i integer);
create temp      table demo_temp      (i integer);

create local temporary table demo_local_temporary (i integer);
create local temp      table demo_local_temp      (i integer);

create global temporary table demo_global_temporary (i integer);
create global temp      table demo_global_temp      (i integer);

create volatile table demo_volatile (i integer);

create table example (col1 number comment 'a column comment') comment='a table comment';

create table testtable_summary (name, summary_amount) as select name, amount1 + amount2 from testtable;

create table testtable_summary (barry char) as select name, amount1 + amount2 from testtable;

create table testtable_summary as select name, amount1 + amount2 from testtable;

create or replace table parquet_col (
  custkey number default null,
  orderdate date default null,
  orderstatus varchar(100) default null,
  price varchar(255)
)
as select
  $1:o_custkey::number,
  $1:o_orderdate::date,
  $1:o_orderstatus::text,
  $1:o_totalprice::text
from @my_stage;

create table collation_demo (
  uncollated_phrase varchar,
  utf8_phrase varchar collate 'utf8',
  english_phrase varchar collate 'en',
  spanish_phrase varchar collate 'sp'
  );


create table mytable
  using template (
    select array_agg(object_construct(*))
      from table(
        infer_schema(
          location=>'@mystage',
          file_format=>'my_parquet_format'
        )
      ));

create table dollar_sign_table (foo$bar boolean);
create table dollar_sign_schema.dollar_sign_table (foo$bar boolean);
CREATE TABLE timestamp_column_default_value_demo (
	timestamp_col1 TIMESTAMP_TZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	timestamp_col2 TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
	timestamp_col3 TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(2),
	sysdate_col4 TIMESTAMP_TZ DEFAULT SYSDATE()
);

create table test_table (test_column NUMBER autoincrement (0, 1));
create table test_schema.test_table (test_column NUMBER autoincrement (0, 1));
create or replace table test_schema.test_table (test_column NUMBER autoincrement (0, 1));
create table test_schema.test_table (test_column INTEGER AUTOINCREMENT);

CREATE TABLE test_table (test_column NUMBER WITH MASKING POLICY my_policy USING(test_column, test_column > 10));

CREATE OR REPLACE TABLE SCHEMA1.TABLE1
(
    "COL1" varchar(128) NOT NULL,
    "COL2" varchar(128) NOT NULL
) CHANGE_TRACKING = TRUE WITH TAG (
    account_objects.tags.IRM = '{"IRM":[{"Primary":"ABC123"}]}'
);
