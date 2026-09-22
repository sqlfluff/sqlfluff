-- GET DIAGNOSTICS, SIGNAL and RESIGNAL statements.
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/get-diagnostics-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/signal-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/resignal-stmt
BEGIN
    GET DIAGNOSTICS rc = ROW_COUNT;
END;

BEGIN
    DECLARE msg STRING;
    GET DIAGNOSTICS CONDITION 1 msg = MESSAGE_TEXT;
END;

BEGIN
    SIGNAL USER_RAISED_EXCEPTION;
END;

BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'nope';
END;

BEGIN
    DECLARE EXIT HANDLER FOR DIVIDE_BY_ZERO BEGIN RESIGNAL; END;
    SELECT 10 / 0;
END;
