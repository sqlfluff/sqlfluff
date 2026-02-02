REVOKE SELECT ON SCHEMA :: Sales TO Vendors;
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
REVOKE IMPERSONATE ON LOGIN::SomeUser TO AnotherUser;
REVOKE CONTROL ON USER::SomeUser TO AnotherUser;

REVOKE GRANT OPTION FOR SELECT, INSERT (Column1)
    ON OBJECT::dbo.SomeObject
    TO SomeUser, AnotherUser
    CASCADE AS SomeAdmin;
GO
