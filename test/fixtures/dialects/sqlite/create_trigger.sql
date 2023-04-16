CREATE TRIGGER update_customer_address UPDATE OF address ON customers
  BEGIN
    UPDATE orders SET address = new.address WHERE customer_name = old.name;
  END;

CREATE TRIGGER cust_addr_chng
INSTEAD OF UPDATE OF cust_addr ON customer_address
BEGIN
  UPDATE customer SET cust_addr=NEW.cust_addr
   WHERE cust_id=NEW.cust_id;
END;

CREATE TRIGGER validate_email_before_insert_leads
   BEFORE INSERT ON leads
BEGIN
   SELECT 1;
END;

CREATE TRIGGER log_contact_after_update
   AFTER UPDATE ON leads
BEGIN
	INSERT INTO lead_logs (
		old_id,
		new_id,
		old_phone,
		new_phone,
		old_email,
		new_email,
		user_action,
		created_at
	)
VALUES
	(
		old.id,
		new.id,
		old.phone,
		new.phone,
		old.email,
		new.email,
		'UPDATE'
	) ;
END;

CREATE TRIGGER aft_insert AFTER INSERT ON emp_details
BEGIN
INSERT INTO emp_log(emp_id,salary,edittime)
         VALUES(NEW.employee_id,NEW.salary,current_date);
END;


