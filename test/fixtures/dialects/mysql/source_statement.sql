-- The SOURCE client command ends at the end of its line, or at an optional ;
SOURCE setup.sql
SOURCE schema/tables.sql;
source ../lib/my-file.v2.sql
Source /var/lib/mysql-files/001_init.sql;
SOURCE C:/db/x.sql
SOURCE path/with spaces/file.sql
SOURCE ~/sql/v(2)/a,b=c@d.sql
\. [x]{y}!%^&*|<>?.sql
SOURCE	tab_separated.sql
\. schema/tables.sql
SELECT 1;
SELECT 2; SOURCE same_line.sql
-- SOURCE is not reserved, so it is still an ordinary identifier.
CREATE TABLE source (source INT);
SELECT source FROM source;
SELECT
    id,
    source
FROM t;
SOURCE last.sql
