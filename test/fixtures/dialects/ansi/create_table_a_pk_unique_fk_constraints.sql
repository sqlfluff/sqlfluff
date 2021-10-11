create table table1 (
    c1 INT,
    c2 INT,
    c3 INT,
    PRIMARY KEY (c1),
    UNIQUE (c2, c3),
    FOREIGN KEY (c2, c3) REFERENCES table2 (c2_, c3_)
)
