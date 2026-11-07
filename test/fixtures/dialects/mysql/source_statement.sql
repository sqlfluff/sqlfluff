SOURCE setup.sql
SOURCE schema/tables.sql;
source lowercase/path.sql
SOURCE path/with spaces/file.sql
SOURCE C:\db\x.sql
SOURCE \\server\share\x.sql
SOURCE a$b.sql
SOURCE a--b.sql
SOURCE a#b.sql
\. schema/tables.sql
\. C:\games\x.sql
SELECT 1; SOURCE same_line.sql;
SOURCE first.sql; SELECT 2;
DELIMITER $$
SOURCE a.sql$$
SOURCE b.sql;
SOURCE C:\db\x.sql;
DELIMITER ;
-- SOURCE is not reserved, so it is still an ordinary identifier.
CREATE TABLE source (source INT);
SELECT source FROM source;
SELECT
    id,
    source
FROM t;
