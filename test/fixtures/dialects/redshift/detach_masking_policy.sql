DETACH MASKING POLICY mask_email
ON customers (email)
FROM PUBLIC;

DETACH MASKING POLICY "customer mask"
ON public.customers (first_name, last_name)
FROM ROLE "analyst role";

DETACH MASKING POLICY analytics.mask_amount
ON analytics.public.sales (amount)
FROM analyst;

DETACH MASKING POLICY mask_name
ON customers (person.name.first_name)
FROM PUBLIC;
