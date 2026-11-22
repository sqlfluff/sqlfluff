-- PRAGMA without arguments
PRAGMA database_list;
PRAGMA show_tables;
PRAGMA enable_progress_bar;

-- PRAGMA called with arguments
PRAGMA table_info('tbl');
PRAGMA storage_info('tbl');

-- PRAGMA assigning a value
PRAGMA table_info = 'tbl';
PRAGMA memory_limit = '100MB';
PRAGMA threads = 2;
pragma force_compression='dict_fsst';

-- PRAGMA with named arguments (full-text search extension)
PRAGMA create_fts_index('documents', 'id', 'body', stemmer = 'porter', stopwords = 'english');
PRAGMA drop_fts_index('documents');
