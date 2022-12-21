-- issue:2094
ALTER VIEW myview ALTER date_column SET DEFAULT NOW();
ALTER VIEW myview ALTER int_column SET DEFAULT 1;
ALTER VIEW myview ALTER text_column SET DEFAULT 'value';
ALTER VIEW myview ALTER bool_column SET DEFAULT false;
ALTER VIEW myview ALTER other_column SET DEFAULT other_value;
ALTER VIEW myview ALTER other_column SET DEFAULT CURRENT_TIMESTAMP;
ALTER VIEW myview ALTER other_column SET DEFAULT a_function(a_parameter);
ALTER VIEW myview ALTER other_column SET DEFAULT a_function('a_parameter');
ALTER VIEW myview ALTER other_column DROP DEFAULT;
ALTER VIEW IF EXISTS myview ALTER date_column SET DEFAULT NOW();
ALTER VIEW IF EXISTS myview ALTER int_column SET DEFAULT 1;
ALTER VIEW IF EXISTS myview ALTER text_column SET DEFAULT 'value';
ALTER VIEW IF EXISTS myview ALTER bool_column SET DEFAULT false;
ALTER VIEW IF EXISTS myview ALTER other_column SET DEFAULT other_value;
ALTER VIEW IF EXISTS myview ALTER other_column SET DEFAULT CURRENT_TIMESTAMP;
ALTER VIEW IF EXISTS myview ALTER other_column SET DEFAULT a_function(a_parameter);
ALTER VIEW IF EXISTS myview ALTER other_column SET DEFAULT a_function('a_parameter');
ALTER VIEW IF EXISTS myview ALTER other_column DROP DEFAULT;

ALTER VIEW myview OWNER TO baz_role;
ALTER VIEW myview OWNER TO "baz-role";
ALTER VIEW myview OWNER TO CURRENT_ROLE;
ALTER VIEW myview OWNER TO CURRENT_USER;
ALTER VIEW myview OWNER TO SESSION_USER;
ALTER VIEW IF EXISTS myview OWNER TO baz_role;
ALTER VIEW IF EXISTS myview OWNER TO "baz-role";
ALTER VIEW IF EXISTS myview OWNER TO CURRENT_ROLE;
ALTER VIEW IF EXISTS myview OWNER TO CURRENT_USER;
ALTER VIEW IF EXISTS myview OWNER TO SESSION_USER;

ALTER VIEW myview RENAME column_name TO new_column_name;
ALTER VIEW myview RENAME COLUMN column_name TO new_column_name;
ALTER VIEW IF EXISTS myview RENAME column_name TO new_column_name;
ALTER VIEW IF EXISTS myview RENAME COLUMN column_name TO new_column_name;

ALTER VIEW myview RENAME TO new_name;
ALTER VIEW IF EXISTS myview RENAME TO new_name;

ALTER VIEW myview SET SCHEMA new_schema;
ALTER VIEW IF EXISTS myview SET SCHEMA new_schema;

ALTER VIEW myview SET ( view_option_name );
ALTER VIEW myview SET ( view_option_name  = 1);
ALTER VIEW myview SET ( view_option_name  = 1, view_option_name2 = 'value', view_option_name3, view_option_name4 = false);
ALTER VIEW IF EXISTS myview SET ( view_option_name );
ALTER VIEW IF EXISTS myview SET ( view_option_name  = 1);
ALTER VIEW IF EXISTS myview SET ( view_option_name, view_option_name2 = 1, view_option_name3);

ALTER VIEW myview RESET ( view_option_name );
ALTER VIEW myview RESET ( view_option_name, view_option_name2 );
ALTER VIEW IF EXISTS myview RESET ( view_option_name );
ALTER VIEW IF EXISTS myview RESET ( view_option_name, view_option_name2 );
