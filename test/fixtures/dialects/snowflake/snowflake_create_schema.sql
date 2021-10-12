create schema mytestschema_clone_restore clone testschema;
create schema mytestschema_clone_restore clone testschema before (timestamp => to_timestamp(40*365*86400));