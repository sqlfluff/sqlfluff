CREATE SYNONYM offices
   FOR hr.locations;

CREATE PUBLIC SYNONYM emp_table
   FOR hr.employees@remote.us.example.com;

CREATE PUBLIC SYNONYM customers FOR oe.customers;
