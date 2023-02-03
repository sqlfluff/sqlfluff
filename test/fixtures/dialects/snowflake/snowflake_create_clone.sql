CREATE DATABASE mytestdb_clone CLONE mytestdb;

CREATE SCHEMA mytestschema_clone CLONE testschema;

CREATE TABLE orders_clone CLONE orders;

CREATE SCHEMA mytestschema_clone_restore CLONE testschema BEFORE (TIMESTAMP => TO_TIMESTAMP(40*365*86400));

CREATE TABLE orders_clone_restore CLONE orders AT (TIMESTAMP => TO_TIMESTAMP_TZ('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));

CREATE TABLE orders_clone_restore CLONE orders BEFORE (STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');
