-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-security-policy-transact-sql

CREATE SECURITY POLICY [FederatedSecurityPolicy]
ADD FILTER PREDICATE [rls].[fn_securitypredicate]([CustomerId])
ON [dbo].[Customer];


CREATE SECURITY POLICY [FederatedSecurityPolicy]
ADD FILTER PREDICATE [rls].[fn_securitypredicate1]([CustomerId])
    ON [dbo].[Customer],
ADD FILTER PREDICATE [rls].[fn_securitypredicate1]([VendorId])
    ON [dbo].[ Vendor],
ADD FILTER PREDICATE [rls].[fn_securitypredicate2]([WingId])
    ON [dbo].[Patient]
WITH (STATE = ON);


CREATE SECURITY POLICY rls.SecPol
    ADD FILTER PREDICATE rls.tenantAccessPredicate(TenantId) ON dbo.Sales,
    ADD BLOCK PREDICATE rls.tenantAccessPredicate(TenantId) ON dbo.Sales AFTER INSERT
;



-- https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-security-policy-transact-sql

ALTER SECURITY POLICY pol1
    ADD FILTER PREDICATE schema_preds.SecPredicate(column1)
    ON myschema.mytable;

ALTER SECURITY POLICY pol1 WITH ( STATE = ON );

ALTER SECURITY POLICY pol1
ADD FILTER PREDICATE schema_preds.SecPredicate1(column1)
    ON myschema.mytable1,
DROP FILTER PREDICATE
    ON myschema.mytable2,
ADD FILTER PREDICATE schema_preds.SecPredicate2(column2, 1)
    ON myschema.mytable3;

ALTER SECURITY POLICY pol1
    ALTER FILTER PREDICATE schema_preds.SecPredicate2(column1)
        ON myschema.mytable;

ALTER SECURITY POLICY rls.SecPol
    ALTER BLOCK PREDICATE rls.tenantAccessPredicate_v2(TenantId)
    ON dbo.Sales AFTER INSERT;



-- https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-security-policy-transact-sql

DROP SECURITY POLICY secPolicy;
