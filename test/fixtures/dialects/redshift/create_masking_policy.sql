CREATE MASKING POLICY mask_email
WITH (email VARCHAR(256))
USING ('hidden'::TEXT);

CREATE MASKING POLICY "customer mask" IF NOT EXISTS
WITH (first_name VARCHAR(100), last_name VARCHAR(100))
USING (UPPER(first_name), 'hidden'::VARCHAR(100));

CREATE MASKING POLICY analytics.mask_amount
WITH (amount DECIMAL(12, 2), authorized BOOLEAN)
USING (CASE WHEN authorized THEN amount ELSE 0 END);
