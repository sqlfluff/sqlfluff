CREATE RLS POLICY policy_concerts
WITH (catgroup VARCHAR(10))
USING (catgroup = 'Concerts');

CREATE RLS POLICY policy_name
WITH (foo VARCHAR(10), bar DECIMAL(10, 2)) AS relation_alias
USING (bar >= 12 AND foo = 'user1');
