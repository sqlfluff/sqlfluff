ENABLE TRIGGER safety ON DATABASE;

ENABLE TRIGGER Person.uAddress ON Person.Address;

ENABLE TRIGGER dbo.tr_insert, dbo.tr_update ON dbo.Orders;

ENABLE TRIGGER ALL ON dbo.Orders;

ENABLE TRIGGER ALL ON ALL SERVER;
