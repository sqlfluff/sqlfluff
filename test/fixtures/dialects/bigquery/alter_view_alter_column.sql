ALTER VIEW example_dataset.example_view
ALTER COLUMN x SET OPTIONS(description="example");

ALTER VIEW IF EXISTS `example-project.example_dataset.example_view`
ALTER COLUMN IF EXISTS x SET OPTIONS(description="example");
