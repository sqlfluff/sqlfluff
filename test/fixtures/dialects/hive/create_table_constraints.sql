CREATE TABLE foo(
    col1 INT PRIMARY KEY,
    col2 INTEGER NOT NULL,
    col3 BIGINT NOT NULL,
    col4 STRING,
    col5 STRING COMMENT 'Column 5'
)
COMMENT 'This is a test table'
STORED AS ORC;

CREATE TABLE product
  (
     product_id        INTEGER,
     product_vendor_id INTEGER,
     PRIMARY KEY (product_id)  DISABLE NOVALIDATE,
     CONSTRAINT product_fk_1 FOREIGN KEY (product_vendor_id) REFERENCES vendor(vendor_id)  DISABLE NOVALIDATE
  );

CREATE TABLE vendor
  (
     vendor_id INTEGER,
     PRIMARY KEY (vendor_id)  DISABLE NOVALIDATE RELY
  );

CREATE TABLE product
  (
     product_id        INTEGER,
     product_vendor_id INTEGER,
     PRIMARY KEY (product_id)  DISABLE NOVALIDATE,
     CONSTRAINT product_fk_1 FOREIGN KEY (product_vendor_id) REFERENCES vendor(vendor_id)  DISABLE NOVALIDATE
  );

CREATE TABLE vendor
  (
     vendor_id INTEGER,
     PRIMARY KEY (vendor_id)  DISABLE NOVALIDATE NORELY
  );
