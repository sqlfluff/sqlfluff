-- Database administration and maintenance statements.

-- https://www.sqlite.org/lang_attach.html
ATTACH DATABASE 'aux.db' AS aux;
ATTACH 'aux.db' AS aux;
ATTACH DATABASE :path AS aux;

-- https://www.sqlite.org/lang_detach.html
DETACH DATABASE aux;
DETACH aux;

-- https://www.sqlite.org/lang_vacuum.html
VACUUM;
VACUUM main;
VACUUM INTO 'backup.db';
VACUUM main INTO 'backup.db';

-- https://www.sqlite.org/lang_reindex.html
REINDEX;
REINDEX nocase;
REINDEX my_table;
REINDEX main.my_index;

-- https://www.sqlite.org/lang_analyze.html
ANALYZE;
ANALYZE main;
ANALYZE my_table;
ANALYZE main.my_index;
