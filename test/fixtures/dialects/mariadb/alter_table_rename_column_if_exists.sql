ALTER TABLE example_error RENAME COLUMN IF EXISTS example_column TO new_name;

ALTER TABLE IF EXISTS `example_error`
RENAME COLUMN IF EXISTS `example_column` TO `new_name`;

ALTER TABLE example_error
RENAME COLUMN IF EXISTS example_column TO new_name,
RENAME COLUMN IF EXISTS other_column TO other_name;

ALTER TABLE example_error RENAME COLUMN example_column TO new_name;
