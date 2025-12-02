CALL mydataset.create_customer();

DECLARE retCode INT64;
-- Procedure signature: (IN account_id STRING, OUT retCode INT64)
CALL mySchema.UpdateSomeTables('someAccountId', retCode);
SELECT retCode;
