GRANT SELECT ON OBJECT::Person.Address TO RosaQdM;
GO

USE AdventureWorks2012;
GRANT EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo
    TO Recruiting11;
GO

GRANT REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee
    TO Wanida WITH GRANT OPTION;
GO

GRANT SELECT ON Person.Address TO RosaQdM;
GO

GRANT SELECT ON Person.Address TO [AdventureWorks2012\RosaQdM];
GO

CREATE ROLE newrole ;
GRANT EXECUTE ON dbo.uspGetBillOfMaterials TO newrole ;
GO

GRANT SELECT ON SCHEMA :: Sales TO Vendors;
GO

REVOKE SELECT ON SCHEMA :: Sales TO Vendors;
GO

DENY SELECT ON OBJECT::Person.Address TO RosaQdM;
GO

DENY EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo
    TO Recruiting11;
GO

DENY REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee
    TO Wanida CASCADE;
GO
