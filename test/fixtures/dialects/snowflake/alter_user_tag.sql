ALTER USER example_user SET TAG my_tag = 'true';

ALTER USER example_user SET TAG db.schema.my_tag = 'true';

ALTER USER IF EXISTS example_user SET TAG db.schema.tag_one = 'a', db.schema.tag_two = 'b';

ALTER USER example_user UNSET TAG my_tag;

ALTER USER example_user UNSET TAG db.schema.my_tag;

ALTER USER IF EXISTS example_user UNSET TAG db.schema.tag_one, db.schema.tag_two;
