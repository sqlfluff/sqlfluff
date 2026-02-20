GRANT SELECT ON OBJECT::Person.Address TO RosaQdM;
GRANT EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo TO Recruiting11;
GRANT REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee TO Wanida WITH GRANT OPTION;
GRANT SELECT ON Person.Address TO RosaQdM;
GRANT SELECT ON Person.Address TO [AdventureWorks2012\RosaQdM];
GRANT EXECUTE ON dbo.uspGetBillOfMaterials TO newrole ;
GRANT SELECT ON SCHEMA :: Sales TO Vendors;
GO

GRANT ALL ON SomeObject TO SomeRole;
GRANT ALL PRIVILEGES ON SomeObject TO [AdventureWorks2012\RosaQdM];
GRANT SELECT, INSERT, UPDATE ON dbo.SomeObject TO SomeRole, SomeOtherRole;
GRANT SELECT (Column1, Column2) ON dbo.SomeTable TO SomeUser;
GRANT SELECT (Column1, Column2), UPDATE (Column2) ON dbo.SomeTable TO SomeUser;
GRANT EXECUTE ON dbo.SomeTableType TO SomeRole WITH GRANT OPTION;
GRANT EXECUTE ON dbo.SomeTableType TO SomeRole AS SomeAdmin;

GRANT ALL ON TYPE::dbo.SomeTableType TO SomeRole;
GRANT ALL ON OBJECT::SomeObject TO SomeRole, AnotherRole;
GRANT ALL ON ASSEMBLY::SomeObject TO SomeRole;
GRANT ALL ON ASYMMETRIC KEY::SomeObject TO SomeRole;
GRANT ALL ON CERTIFICATE::SomeObject TO SomeRole;
GRANT ALL ON TYPE::SomeObject TO SomeRole;
GRANT ALL ON DATABASE::SomeObject TO SomeRole;
GRANT ALL ON FULLTEXT CATALOG::SomeObject TO SomeRole;
GRANT ALL ON FULLTEXT STOPLIST::SomeObject TO SomeRole;
GRANT ALL ON ROLE::SomeObject TO SomeRole;
GRANT ALL ON SEARCH PROPERTY LIST::SomeObject TO SomeRole;
GRANT ALL ON SYMMETRIC KEY::SomeObject TO SomeRole;
GRANT ALL ON XML SCHEMA COLLECTION::SomeObject TO SomeRole;
GRANT IMPERSONATE ON LOGIN::SomeUser TO AnotherUser;
GRANT CONTROL ON USER::SomeUser TO AnotherUser;

GRANT SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    WITH GRANT OPTION AS SomeAdmin;
GO
