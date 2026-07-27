SELECT name, age FROM people UNION VALUES ('John Doe' AS name, 31 AS age), ('Jane Doe', 31);

SELECT name, age FROM people UNION VALUES ('John Doe' AS name, 31);

SELECT name, age FROM people UNION VALUES (DEFAULT, 31);

SELECT name, age FROM people UNION VALUES ('John', 31), (DEFAULT as name, 21 as age);

INSERT INTO people VALUES ('John Doe' as name, DEFAULT as age);

INSERT INTO people VALUES ('John Doe' as name, 31 as age), ('Jane Doe' as name, 31 as age);

INSERT INTO people VALUES ('John Doe' as name, 31), ('Jane Doe' as name, 31 as age);
