ALTER MASKING POLICY test_policy
USING ('XXXX'::TEXT);

ALTER MASKING POLICY db1.mask_email
USING (LEFT(SPLIT_PART(email, '@', 1), 1) || '****@' || SPLIT_PART(email, '@', 2));
