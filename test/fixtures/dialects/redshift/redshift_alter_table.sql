ALTER TABLE example_table
    ADD CONSTRAINT example_name PRIMARY KEY (example_sk);

alter table users
rename to users_bkup;

alter table venue
owner to dwuser;

alter table vdate owner to vuser;

alter table venue
rename column venueseats to venuesize;

alter table category
drop constraint category_pkey;

alter table event alter column eventname type varchar(300);

create table t1(c0 int encode lzo, c1 bigint encode zstd, c2 varchar(16) encode lzo, c3 varchar(32) encode zstd);

alter table t1 alter column c0 encode az64;

alter table t1 alter column c1 encode az64;

alter table t1 alter column c2 encode bytedict;

alter table t1 alter column c3 encode runlength;

alter table inventory alter diststyle key distkey inv_warehouse_sk;

alter table inventory alter distkey inv_item_sk;

alter table inventory alter diststyle all;

alter table t1 alter sortkey(c0, c1);

alter table t1 alter sortkey none;

alter table t1 alter sortkey(c0, c1);

alter table t1 alter encode auto;

alter table t2 alter column c0 encode lzo;

ALTER TABLE the_schema.the_table ADD COLUMN the_timestamp TIMESTAMP;

ALTER TABLE the_schema.the_table ADD COLUMN the_boolean BOOLEAN DEFAULT FALSE;

alter table users
add column feedback_score int
default NULL;

alter table users drop column feedback_score;

alter table users
drop column feedback_score cascade;
