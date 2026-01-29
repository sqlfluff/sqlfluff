GRANT SELECT ON OBJECT::Person.Address TO RosaQdM;
GRANT EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo
    TO Recruiting11;
GRANT REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee
    TO Wanida WITH GRANT OPTION;
GRANT SELECT ON Person.Address TO RosaQdM;
GRANT SELECT ON Person.Address TO [AdventureWorks2012\RosaQdM];

GRANT EXECUTE ON dbo.uspGetBillOfMaterials TO newrole ;
GRANT SELECT ON SCHEMA :: Sales TO Vendors;
REVOKE SELECT ON SCHEMA :: Sales TO Vendors;
DENY SELECT ON OBJECT::Person.Address TO RosaQdM;
DENY EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo
    TO Recruiting11;
DENY REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee
    TO Wanida CASCADE;
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

GRANT SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    WITH GRANT OPTION AS SomeAdmin;
GO

DENY ALL ON SomeObject TO SomeRole;
DENY ALL PRIVILEGES ON SomeObject TO [AdventureWorks2012\RosaQdM];
DENY SELECT, INSERT, UPDATE ON dbo.SomeObject TO SomeRole, SomeOtherRole;
DENY SELECT (Column1, Column2) ON dbo.SomeTable TO SomeUser;
DENY SELECT (Column1, Column2), UPDATE (Column2) ON dbo.SomeTable TO SomeUser;
DENY EXECUTE ON dbo.SomeTableType TO SomeRole CASCADE;
DENY EXECUTE ON dbo.SomeTableType TO SomeRole AS SomeAdmin;

DENY ALL ON TYPE::dbo.SomeTableType TO SomeRole;
DENY ALL ON OBJECT::SomeObject TO SomeRole, AnotherRole;
DENY ALL ON ASSEMBLY::SomeObject TO SomeRole;
DENY ALL ON ASYMMETRIC KEY::SomeObject TO SomeRole;
DENY ALL ON CERTIFICATE::SomeObject TO SomeRole;
DENY ALL ON TYPE::SomeObject TO SomeRole;
DENY ALL ON DATABASE::SomeObject TO SomeRole;
DENY ALL ON FULLTEXT CATALOG::SomeObject TO SomeRole;
DENY ALL ON FULLTEXT STOPLIST::SomeObject TO SomeRole;
DENY ALL ON ROLE::SomeObject TO SomeRole;
DENY ALL ON SEARCH PROPERTY LIST::SomeObject TO SomeRole;
DENY ALL ON SYMMETRIC KEY::SomeObject TO SomeRole;
DENY ALL ON XML SCHEMA COLLECTION::SomeObject TO SomeRole;

DENY SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    CASCADE AS SomeAdmin;
GO

REVOKE ALL ON SomeObject TO SomeRole;
REVOKE ALL ON SomeObject FROM SomeRole;
REVOKE ALL PRIVILEGES ON SomeObject TO [AdventureWorks2012\RosaQdM];
REVOKE SELECT, INSERT, UPDATE ON dbo.SomeObject TO SomeRole, SomeOtherRole;
REVOKE SELECT (Column1, Column2) ON dbo.SomeTable TO SomeUser;
REVOKE SELECT (Column1, Column2), UPDATE (Column2) ON dbo.SomeTable TO SomeUser;
REVOKE EXECUTE ON dbo.SomeTableType TO SomeRole CASCADE;
REVOKE EXECUTE ON dbo.SomeTableType TO SomeRole AS SomeAdmin;
REVOKE GRANT OPTION FOR EXECUTE ON dbo.SomeTableType TO SomeRole AS SomeAdmin;

REVOKE ALL ON TYPE::dbo.SomeTableType TO SomeRole;
REVOKE ALL ON OBJECT::SomeObject TO SomeRole, AnotherRole;
REVOKE ALL ON ASSEMBLY::SomeObject TO SomeRole;
REVOKE ALL ON ASYMMETRIC KEY::SomeObject TO SomeRole;
REVOKE ALL ON CERTIFICATE::SomeObject TO SomeRole;
REVOKE ALL ON TYPE::SomeObject TO SomeRole;
REVOKE ALL ON DATABASE::SomeObject TO SomeRole;
REVOKE ALL ON FULLTEXT CATALOG::SomeObject TO SomeRole;
REVOKE ALL ON FULLTEXT STOPLIST::SomeObject TO SomeRole;
REVOKE ALL ON ROLE::SomeObject TO SomeRole;
REVOKE ALL ON SEARCH PROPERTY LIST::SomeObject TO SomeRole;
REVOKE ALL ON SYMMETRIC KEY::SomeObject TO SomeRole;
REVOKE ALL ON XML SCHEMA COLLECTION::SomeObject TO SomeRole;

REVOKE GRANT OPTION FOR SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    CASCADE AS SomeAdmin;
GO
