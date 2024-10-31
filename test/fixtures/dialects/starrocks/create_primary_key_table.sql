create table users (
    user_id bigint NOT NULL,
    name string NOT NULL,
    email string NULL,
    address string NULL,
    age tinyint NULL,
    sex tinyint NULL,
    last_active datetime,
    property0 tinyint NOT NULL,
    property1 tinyint NOT NULL,
    property2 tinyint NOT NULL,
    property3 tinyint NOT NULL
) 
PRIMARY KEY (`user_id`)
DISTRIBUTED BY HASH(`user_id`)
ORDER BY(`address`,`last_active`)
PROPERTIES(
    "replication_num" = "3",
    "enable_persistent_index" = "true"
);
