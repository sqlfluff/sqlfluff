-- show all the user specified properties for table `customer`
SHOW TBLPROPERTIES customer;

-- show all the user specified properties for a qualified table `customer`
-- in database `salesdb`
SHOW TBLPROPERTIES salesdb.customer;

-- show value for unquoted property key `created.by.user`
SHOW TBLPROPERTIES customer (created.by.user);

-- show value for property `created.date`` specified as string literal
SHOW TBLPROPERTIES customer ('created.date');
