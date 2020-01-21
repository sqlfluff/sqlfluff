create table table1 (
    c1 INT NOT NULL,
    c2 INT NULL DEFAULT 1,
    c3 INT PRIMARY KEY,
    c4 INT UNIQUE,
    c5 INT REFERENCES table2,
    c6 INT REFERENCES table2 (c6_other),
    c7 INT NOT NULL DEFAULT 1 UNIQUE REFERENCES table3 (c7_other)
)
