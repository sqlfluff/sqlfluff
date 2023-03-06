
/*
Rules set to none test

The previous default setting for rules was
'None' which meant all rules would be run. The
new default is 'all', but having rules = None should
still run all rules, meaning this query will trigger
LT13,AM04, and CP01
*/

SELECT * from bar
