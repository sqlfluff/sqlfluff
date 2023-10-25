ALTER MASKING POLICY IF EXISTS "a quoted policy name" RENAME TO a_sane_name;

ALTER MASKING POLICY email_mask SET BODY ->
  CASE
  WHEN current_role() IN ('ANALYST') THEN VAL
  ELSE sha2(VAL, 512)
  END
;

ALTER MASKING POLICY aggressively_mask_pii SET TAG environment = 'silver' , silo = 'sales';

ALTER MASKING POLICY IF EXISTS mask_pii_policy UNSET TAG environment, billing;

ALTER MASKING POLICY db.sch.fully_redacted_policy SET COMMENT = 'A super strict policy';

ALTER MASKING POLICY IF EXISTS mask_pii_policy UNSET COMMENT;
