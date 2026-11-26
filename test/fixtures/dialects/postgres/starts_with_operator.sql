SELECT 'alphabet' ^@ 'alph';

SELECT 'alphabet'^@'alph';

SELECT first_name
FROM customers
WHERE first_name ^@ 'Jo' AND NOT last_name ^@ 'Sm';

SELECT 'alphabet' OPERATOR(pg_catalog.^@) 'alph';
