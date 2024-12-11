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

CREATE TABLE my_table (
  foo TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP::TIMESTAMP_NTZ
)
;

CREATE TABLE IF NOT EXISTS EXAMPLE_TABLE
(
    EXAMPLE VARCHAR AUTOINCREMENT START 1 INCREMENT 1 ORDER
);

CREATE TABLE IF NOT EXISTS EXAMPLE_TABLE
(
    EXAMPLE VARCHAR AUTOINCREMENT START 1 INCREMENT 1 NOORDER
);

CREATE OR REPLACE DYNAMIC TABLE names
TARGET_LAG = '1 minute'
WAREHOUSE = mywh
AS
SELECT var:id::int id, var:fname::string first_name,
var:lname::string last_name FROM raw;

CREATE OR REPLACE DYNAMIC TABLE names
TARGET_LAG = '1 minute'
REFRESH_MODE = AUTO
INITIALIZE = ON_CREATE
WAREHOUSE = mywh
AS
SELECT var:id::int id, var:fname::string first_name,
var:lname::string last_name FROM raw;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_DOWNSTREAM_LAG
TARGET_LAG = DOWNSTREAM
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_DOWNSTREAM_QUOTED_LITERAL_LAG
TARGET_LAG = 'DOWNSTREAM'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_SINGLE_SECOND_LAG
TARGET_LAG = '1 second'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_MULTIPLE_SECONDS_LAG
TARGET_LAG = '5 seconds'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_SINGLE_MINUTE_LAG
TARGET_LAG = '1 minute'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_MULTIPLE_MINUTES_LAG
TARGET_LAG = '5 minutes'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_SINGLE_HOUR_LAG
TARGET_LAG = '1 hour'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_MULTIPLE_HOURS_LAG
TARGET_LAG = '5 hours'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_SINGLE_DAY_LAG
TARGET_LAG = '1 day'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE DYNAMIC TABLE DT_WITH_MULTIPLE_DAYS_LAG
TARGET_LAG = '5 days'
WAREHOUSE = mywh
AS
SELECT * FROM my_table;

CREATE OR REPLACE TABLE IF NOT EXISTS EXAMPLE_TABLE_WITH_RLS (
  EXAMPLE VARCHAR
  ) WITH ROW ACCESS POLICY my_db.my_schema.rls_policy ON (EXAMPLE);

CREATE OR REPLACE TABLE IF NOT EXISTS EXAMPLE_TABLE_WITH_RLS (
  EXAMPLE VARCHAR
) WITH ROW ACCESS POLICY rls_policy ON (EXAMPLE);

CREATE TABLE IDENTIFIER(:SOME_TABLE) (AMOUNT NUMBER);

CREATE OR REPLACE TEMP TABLE mytable (
  id INTEGER NOT NULL PRIMARY KEY ENABLE ENFORCED VALIDATE RELY
);

CREATE OR REPLACE TABLE myschema.mytable (
  id INTEGER NOT NULL
  , CONSTRAINT mytable_pk PRIMARY KEY (id) NOT ENFORCED NOVALIDATE NORELY
);

CREATE TABLE some_schema.some_table
(
  is_condition_true BOOLEAN
  , some_text_value VARCHAR(100)
  , some_event_date_time_utc VARCHAR AS (TO_TIMESTAMP(SUBSTR(some_text_value, 5, 13)))
  , some_other_event_date_time_utc TIMESTAMP AS (IFF(is_condition_true AND TRY_TO_NUMBER(some_text_value) IS NOT NULL, TO_TIMESTAMP(SUBSTR(some_text_value, 5, 13)), '1900-01-01')) COMMENT 'The date and time of the other event'
);


CREATE OR REPLACE TABLE some_table (
  id INTEGER NOT NULL,
  CONSTRAINT MY_FK FOREIGN KEY (id) REFERENCES another_table(id) MATCH SIMPLE ON DELETE RESTRICT
);

CREATE OR REPLACE TABLE some_table (
  id INTEGER NOT NULL,
  CONSTRAINT MY_FK FOREIGN KEY (id) REFERENCES another_table MATCH FULL ON DELETE RESTRICT
);


CREATE OR REPLACE TABLE some_table (
    ID INTEGER NOT NULL CONSTRAINT MY_FK
    FOREIGN KEY REFERENCES another_table (id)
    MATCH PARTIAL
    ON DELETE RESTRICT
    ON UPDATE SET DEFAULT
);

CREATE OR REPLACE TABLE some_table (
    ID INTEGER NOT NULL,
    CONSTRAINT MY_FK FOREIGN KEY (ID) REFERENCES another_table (id)
    MATCH SIMPLE
    ON DELETE CASCADE
);

CREATE OR ALTER TABLE some_table (
  id INTEGER NOT NULL
);
