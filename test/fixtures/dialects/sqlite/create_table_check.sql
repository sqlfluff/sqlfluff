CREATE TABLE foo(
    num NUMBER NOT NULL,
    CHECK (num > 0)
);
