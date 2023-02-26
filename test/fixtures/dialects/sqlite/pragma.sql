PRAGMA analysis_limit = 7;

PRAGMA schema.application_id;

PRAGMA schema.auto_vacuum = INCREMENTAL;

PRAGMA automatic_index = TRUE;

PRAGMA schema.cache_size = -500;

PRAGMA collation_list;

PRAGMA data_store_directory = 'directory-name';

PRAGMA encoding = 'UTF-16be';

PRAGMA schema.foreign_key_check('table-name');

PRAGMA schema.journal_mode = WAL;

PRAGMA schema.locking_mode = NORMAL;

PRAGMA schema.secure_delete = FAST;

PRAGMA schema.synchronous = 0;

PRAGMA temp_store = DEFAULT;

PRAGMA schema.wal_checkpoint(FULL);
