ATTACH MASKING POLICY mask_email
ON customers (email)
TO PUBLIC;

ATTACH MASKING POLICY "customer mask"
ON public.customers (first_name, last_name)
USING (given_name, family_name)
TO ROLE "analyst role"
PRIORITY 10;

ATTACH MASKING POLICY analytics.mask_amount
ON analytics.public.sales (amount)
USING (amount, authorized)
TO analyst
PRIORITY 20;

ATTACH MASKING POLICY mask_name
ON customers (person.name.first_name)
USING (person.name.first_name)
TO PUBLIC;
