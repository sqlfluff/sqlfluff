CREATE SCHEMA dataset_name;

CREATE SCHEMA IF NOT EXISTS project_name.dataset_name
DEFAULT COLLATE 'und:ci'
OPTIONS(description="example");
