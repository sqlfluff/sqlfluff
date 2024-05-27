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
