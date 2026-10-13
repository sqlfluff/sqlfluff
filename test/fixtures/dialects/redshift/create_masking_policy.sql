CREATE MASKING POLICY test_policy
WITH (col1 varchar)
USING ('***'::TEXT);

CREATE MASKING POLICY IF NOT EXISTS mask_email
WITH (email VARCHAR(100))
USING (LEFT(SPLIT_PART(email, '@', 1), 2) || '---@' || SPLIT_PART(email, '@', 2));

CREATE MASKING POLICY db1.hash_credit
WITH (credit_card VARCHAR(256), salt VARCHAR(64))
USING (sha2(credit_card + salt, 256));
