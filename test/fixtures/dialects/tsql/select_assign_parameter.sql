select userid = c.id
from
	mydb.myschema.customer c
where
	c.name = 'drjwelch';

select @userid_parameter = c.id
from
	mydb.myschema.customer c
where
	c.name = 'drjwelch';

-- Multiple variable assignments in one SELECT
SELECT TOP 1
	@potential_match = [id],
	@full_name = CONCAT(first_name, ' ', surname)
FROM [dbo].[authors];

-- Compound assignment operators
SELECT @counter += 1, @sum += amount
FROM transactions;

SELECT @result *= factor
FROM coefficients
WHERE id = 1;

SELECT @text_concat = @text_concat + ', ' + description
FROM items;

-- Variable assignment with subquery
SELECT @max_price = (SELECT MAX(price) FROM products)
FROM dual;

-- Mix of variable assignment and regular select
DECLARE @var1 INT, @var2 VARCHAR(50);
SELECT @var1 = id, @var2 = name, description
FROM employees
WHERE emp_id = 100;
