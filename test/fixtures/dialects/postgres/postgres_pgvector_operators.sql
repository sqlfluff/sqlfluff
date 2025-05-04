SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 5;

SELECT * FROM items ORDER BY embedding <+> '[3,1,2]' LIMIT 5;

SELECT * FROM items ORDER BY embedding <#> '[3,1,2]' LIMIT 5;