-- Package body with only BEGIN...END initialization block (no declarations)
CREATE OR REPLACE PACKAGE BODY empty_package AS
BEGIN
  NULL;
END empty_package;
/

-- Package body with only IS and direct END (minimal)
CREATE PACKAGE BODY minimal_package IS
END minimal_package;
/
