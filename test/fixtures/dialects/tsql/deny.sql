DENY SELECT ON OBJECT::Person.Address TO RosaQdM;
DENY EXECUTE ON OBJECT::HumanResources.uspUpdateEmployeeHireInfo TO Recruiting11;
DENY REFERENCES (BusinessEntityID) ON OBJECT::HumanResources.vEmployee TO Wanida CASCADE;
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
DENY IMPERSONATE ON LOGIN::SomeUser TO AnotherUser;
DENY CONTROL ON USER::SomeUser TO AnotherUser;

DENY SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    CASCADE AS SomeAdmin;
GO
