-- Indented INSERT target with nested VALUES rows.
INSERT INTO
    assets (
        id,
        filename,
        mime_type
    )
VALUES
    (1, 'file.txt', 'text/plain'),
    (2, 'image.png', 'image/png');

INSERT INTO foo (bar, baz) VALUES (1, 2), (3, 4);
