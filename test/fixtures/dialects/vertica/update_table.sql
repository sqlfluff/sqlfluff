UPDATE fact SET price = price - cost * 80 WHERE cost > 100;
UPDATE retail.customer SET state = 'NH' WHERE CID > 100;
UPDATE addresses SET address='New Address'
   WHERE cust_id IN (SELECT new_cust_id FROM new_addresses WHERE new_address='T');
