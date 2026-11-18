DESCRIBE TABLE customer;

DESCRIBE customer;

DESCRIBE TABLE salesdb.customer;

DESCRIBE TABLE EXTENDED customer;

DESCRIBE TABLE EXTENDED customer PARTITION (state = 'AR');

DESCRIBE customer salesdb.customer.name;

DESCRIBE TABLE customer salesdb.customer.name;

DESCRIBE TABLE customer customer.name;

DESCRIBE TABLE customer name;

-- `history` and `detail` are not reserved, so a table may be named either.
DESCRIBE history.tbl;

DESCRIBE detail.tbl;

DESCRIBE history;

DESCRIBE detail;
