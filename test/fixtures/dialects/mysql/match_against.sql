SELECT * FROM articles WHERE MATCH (title, body) AGAINST ('database');

SELECT * FROM articles
WHERE MATCH (title, body) AGAINST ('database' IN NATURAL LANGUAGE MODE);

SELECT * FROM articles
WHERE MATCH (title, body) AGAINST ('database' IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION);

SELECT * FROM articles
WHERE MATCH (title, body) AGAINST ('+MySQL -YourSQL' IN BOOLEAN MODE);

SELECT * FROM articles
WHERE MATCH (title, body) AGAINST ('database' WITH QUERY EXPANSION);

SELECT
    id,
    MATCH (title, body) AGAINST ('Tutorial') AS score
FROM articles
ORDER BY score DESC;
