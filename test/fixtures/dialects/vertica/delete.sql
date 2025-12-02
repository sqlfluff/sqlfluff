-- https://docs.vertica.com/latest/en/sql-reference/statements/delete/#examples
DELETE FROM temp1;

DELETE FROM retail.customer WHERE state IN ('MA', 'NH');

DELETE FROM new_addresses
WHERE new_cust_id IN (SELECT cust_id FROM addresses WHERE address='New Address');
