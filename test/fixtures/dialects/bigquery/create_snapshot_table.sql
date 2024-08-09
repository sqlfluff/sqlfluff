CREATE SNAPSHOT TABLE `example-project.example_dataset.example_table_snapshot_20240101`
CLONE `example-project.example_dataset.example_table`;

CREATE SNAPSHOT TABLE IF NOT EXISTS `example-project.example_dataset.example_table_snapshot_20240101`
CLONE `example-project.example_dataset.example_table`
FOR SYSTEM_TIME AS OF TIMESTAMP("2024-01-01 12:00:00")
OPTIONS (
    expiration_timestamp=TIMESTAMP("2024-02-01 12:00:00"),
    friendly_name="my_table_snapshot",
    description="example description",
    labels=[("example_key", "example_value")]
);
