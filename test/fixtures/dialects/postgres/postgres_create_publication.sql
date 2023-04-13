CREATE PUBLICATION abc;

CREATE PUBLICATION abc FOR ALL TABLES;

CREATE PUBLICATION abc FOR TABLE def;

CREATE PUBLICATION abc FOR TABLE def, sch.ghi;

CREATE PUBLICATION abc FOR TABLE def, TABLE sch.ghi;

CREATE PUBLICATION abc FOR TABLE def*;

CREATE PUBLICATION abc FOR
    TABLE a,
    TABLE aa, ab, ac,
    TABLE ONLY b,
    TABLE c*,
    TABLE ca*, cb*,
    TABLE ONLY (d),
    TABLE e (col1),
    TABLE f (col2, col3),
    TABLE g* (col4, col5),
    TABLE h WHERE (col6 > col7),
    TABLE i (col8, col9) WHERE (col10 > col11),
    TABLES IN SCHEMA j,
    TABLES IN SCHEMA k,
    TABLES IN SCHEMA CURRENT_SCHEMA, l, m,
    TABLES IN SCHEMA n, o, p;

CREATE PUBLICATION abc FOR TABLE a, b
    WITH (publish = 'insert,update', publish_via_partition_root = TRUE);

CREATE PUBLICATION abc FOR TABLE a, b
    WITH (publish_via_partition_root = TRUE);

CREATE PUBLICATION abc FOR TABLE a, b
    WITH (publish = 'insert,update');

CREATE PUBLICATION abc WITH (publish = 'insert,update');

-- examples from https://www.postgresql.org/docs/15/sql-createpublication.html

CREATE PUBLICATION mypublication FOR TABLE users, departments;

CREATE PUBLICATION active_departments FOR TABLE departments WHERE (active IS TRUE);

CREATE PUBLICATION alltables FOR ALL TABLES;

CREATE PUBLICATION insert_only FOR TABLE mydata
    WITH (publish = 'insert');

CREATE PUBLICATION production_publication FOR TABLE users, departments, TABLES IN SCHEMA production;

CREATE PUBLICATION sales_publication FOR TABLES IN SCHEMA marketing, sales;

CREATE PUBLICATION users_filtered FOR TABLE users (user_id, firstname);
