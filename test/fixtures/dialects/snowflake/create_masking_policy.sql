CREATE OR REPLACE MASKING POLICY
        XXXX.XX.example_MASKING_POLICY AS (val VARCHAR) RETURNS VARCHAR ->
      CASE WHEN is_role_in_session('SNOWFLAKE_PII')
        THEN val
        ELSE '*** masked ***'
      END
      COMMENT = 'Applied 2021-07-13T03:12:16+0000';

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    else '*********'
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_account() in ('<prod_account_identifier>') then val
    else '*********'
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() IN ('ANALYST') then val
    else NULL
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    else '********'
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    else sha2(val) -- return hash of the column value
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    when current_role() in ('SUPPORT') then regexp_replace(val,'.+\@','*****@') -- leave email domain unmasked
    else '********'
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('SUPPORT') then val
    else date_from_parts(0001, 01, 01)::timestamp_ntz -- returns 0001-01-01 00:00:00.000
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    else mask_udf(val) -- custom masking function
  end;

create or replace masking policy email_mask as (val string) returns string ->
  case
    when current_role() in ('ANALYST') then val
    else object_insert(val, 'USER_IPADDRESS', '****', true)
  end;
