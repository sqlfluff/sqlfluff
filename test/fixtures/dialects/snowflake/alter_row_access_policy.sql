ALTER ROW ACCESS POLICY my_access_policy RENAME TO other_access_policy;

ALTER ROW ACCESS POLICY IF EXISTS my_access_policy RENAME TO other_access_policy;

ALTER ROW ACCESS POLICY my_access_policy SET BODY -> EXISTS(some_val);

ALTER ROW ACCESS POLICY my_access_policy SET TAG tag_name = 'tag_value';

ALTER ROW ACCESS POLICY my_access_policy SET TAG tag_name = 'tag_value', tag_name = 'tag_value';

ALTER ROW ACCESS POLICY my_access_policy UNSET TAG tag_name, tag_name;

ALTER ROW ACCESS POLICY my_access_policy SET COMMENT = 'comment';

ALTER ROW ACCESS POLICY my_access_policy UNSET COMMENT;
