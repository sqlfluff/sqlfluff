create schema mytestschema_clone_restore clone testschema;
create schema mytestdatabase1.mytestschema_clone_restore clone mytestdatabase2.testschema;
create schema mytestschema_clone_restore clone testschema before (timestamp => to_timestamp(40*365*86400));
create schema mytestschema comment = 'My test schema.';
create schema mytestschema tag (tag1 = 'foo', tag2 = 'bar');
create schema mytestschema with managed access;
create transient schema if not exists mytestschema default_ddl_collation = 'de_DE';
