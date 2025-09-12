-- Multiple PRAGMA statements with inconsistent indentation
PRAGMA foreign_keys = ON;
    PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
  PRAGMA cache_size = 10000;

-- Multi-line statements with PRAGMA
SELECT
name,
sql
FROM sqlite_master
WHERE type = 'table'
AND name IS NOT 'sqlite_sequence'
ORDER BY name;

PRAGMA table_info(users);
