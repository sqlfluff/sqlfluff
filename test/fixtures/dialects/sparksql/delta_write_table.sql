-- append
INSERT INTO default.people10m SELECT * FROM more_people;

-- overwrite
INSERT OVERWRITE TABLE default.people10m SELECT * FROM more_people;

-- with user-defined commit metadata
SET spark.databricks.delta.commitInfo.userMetadata = "overwritten-for-fixing-incorrect-data";
INSERT OVERWRITE default.people10m SELECT * FROM more_people;
