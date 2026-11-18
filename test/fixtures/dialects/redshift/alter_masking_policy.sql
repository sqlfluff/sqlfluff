ALTER MASKING POLICY mask_email USING ('redacted'::TEXT);

ALTER MASKING POLICY analytics."customer mask"
USING (LOWER(first_name), LOWER(last_name));

ALTER MASKING POLICY mask_amount
USING (CASE WHEN authorized THEN amount ELSE NULL END);
