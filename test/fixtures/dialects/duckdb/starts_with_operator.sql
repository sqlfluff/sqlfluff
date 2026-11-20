SELECT 'abcdef' ^@ 'abc';

SELECT 'abcdef'^@'abc';

SELECT first_name
FROM customers
WHERE first_name ^@ 'Jo' AND NOT last_name ^@ 'Sm';
