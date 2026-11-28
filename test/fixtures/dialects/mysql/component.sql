INSTALL COMPONENT 'file://component_validate_password';
INSTALL COMPONENT 'file://component1', 'file://component2';
INSTALL COMPONENT 'file://component1', 'file://component2'
SET GLOBAL component1.var1 = 12 + 3, PERSIST component2.var2 = 'strings';
UNINSTALL COMPONENT 'file://component_validate_password';
UNINSTALL COMPONENT 'file://component1', 'file://component2';
