-- T-SQL alternative alias syntax (AltAliasExpression)

select userid = c.id
from
	mydb.myschema.customer c
where
	c.name = 'drjwelch';

-- T-SQL parameter assignment, previously (<3.1.0) parsed as AltAliasExpression

select @userid_parameter = c.id
from
	mydb.myschema.customer c
where
	c.name = 'drjwelch';

-- T-SQL parameter assignment from sequence

select @userid_parameter = NEXT VALUE FOR myschema.customer_ids;

-- NULL assignment to parameter using SELECT is not linted as a comparison (issue #6000)

select @userid_parameter = NULL;
