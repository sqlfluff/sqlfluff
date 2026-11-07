-- Indented INSERT target with nested VALUES rows.
INSERT INTO
    tbl (
        col1,
        col2
    )
VALUES
    (1, 2),
    (3, 4);

INSERT INTO tbl (col1) VALUES (1);
