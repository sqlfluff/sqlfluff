CREATE VIEW my_view as (select x from t) COMMENT IS 'nice view';
CREATE VIEW my_view (col1 ) as (select x from t);
CREATE OR REPLACE FORCE VIEW my_view as select y from t;
CREATE OR REPLACE VIEW my_view (col_1 COMMENT IS 'something important',col2) as select max(y) from t;
CREATE VIEW schem.few (col1 )
/* some view
header */
as (select x from t);
CREATE VIEW schem.few (col1 )
--- single line
as (select x from t);
---
CREATE VIEW T AS SELECT * FROM A COMMENT IS 'BLABLA';
