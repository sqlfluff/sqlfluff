CREATE TABLE t_table1
(
    x INT64,
    PRIMARY KEY (x) NOT ENFORCED
)
;
CREATE TABLE t_table1
(
    y STRING,
    FOREIGN KEY (y) REFERENCES t_table2(y) NOT ENFORCED,
)
;
CREATE TABLE t_table1
(
    x INT64,
    PRIMARY KEY (x) NOT ENFORCED,
    y STRING,
    FOREIGN KEY (y) REFERENCES t_table2(y) NOT ENFORCED,
    _other STRING
)
;

CREATE TABLE `some_dataset.some_table` (
    id STRING NOT NULL PRIMARY KEY NOT ENFORCED,
    other_field STRING REFERENCES other_table(other_field) NOT ENFORCED
);
