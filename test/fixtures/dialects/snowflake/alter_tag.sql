ALTER TAG my_tag SET MASKING POLICY policy_name;

ALTER TAG IF EXISTS my_tag SET MASKING POLICY policy_name;

ALTER TAG my_tag SET MASKING POLICY policy_name, MASKING POLICY policy_name_2, MASKING POLICY policy_name_3;

ALTER TAG my_tag SET COMMENT = 'this is a comment';

ALTER TAG my_tag UNSET COMMENT;

ALTER TAG my_tag ADD ALLOWED_VALUES 'my_value';

ALTER TAG my_tag ADD ALLOWED_VALUES 'my_value', 'my_value_2';

ALTER TAG my_tag DROP ALLOWED_VALUES 'my_value';

ALTER TAG my_tag DROP ALLOWED_VALUES 'my_value', 'my_value_2';

ALTER TAG my_tag UNSET ALLOWED_VALUES;
