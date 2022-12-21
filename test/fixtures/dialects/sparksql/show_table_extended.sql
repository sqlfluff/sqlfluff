-- Show the details of the table
SHOW TABLE EXTENDED LIKE 'employee';

-- showing the multiple table details with pattern matching
SHOW TABLE EXTENDED LIKE 'employe*';

-- show partition file system details
SHOW TABLE EXTENDED IN default LIKE 'employee' PARTITION (grade = 1);

-- show partition file system details with pattern matching
SHOW TABLE EXTENDED IN default LIKE 'empl*' PARTITION (grade = 1);
