ALTER ORGANIZATION
SET OPTIONS (`region-us.default_time_zone`="Asia/Tokyo");

ALTER PROJECT `example-project`
SET OPTIONS (`region-us.default_time_zone`="Asia/Tokyo");

ALTER BI_CAPACITY `example-project.region-us.default`
SET OPTIONS(size_gb = 250);

ALTER CAPACITY `example-project.region-us.example_commitment`
SET OPTIONS (plan = "THREE_YEAR");

ALTER RESERVATION `example-project.region-us.example_reservation`
SET OPTIONS (slot_capacity=123);
