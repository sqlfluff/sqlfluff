ALTER SCHEMA example_dataset
SET DEFAULT COLLATE "und:ci";

ALTER SCHEMA example_dataset
SET OPTIONS(description="");

ALTER SCHEMA example_dataset
ADD REPLICA `EU` OPTIONS(location=`eu`);

ALTER SCHEMA example_dataset
DROP REPLICA `EU`;
