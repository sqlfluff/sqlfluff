create table table1 (
    c1 INT NOT NULL,
    c2 INT NULL,
    c3 INT DEFAULT 'a',
    c4 FLOAT,
    PRIMARY KEY (c1),
    UNIQUE (c2, c3),
    FOREIGN KEY (c2, c3) REFERENCES table2 (c2_, c3_)
)
