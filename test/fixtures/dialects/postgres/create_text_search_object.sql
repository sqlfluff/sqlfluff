CREATE TEXT SEARCH DICTIONARY my_english (
    TEMPLATE = snowball,
    LANGUAGE = english,
    STOPWORDS = english
);

CREATE TEXT SEARCH DICTIONARY public.simple_dict (
    TEMPLATE = pg_catalog.simple,
    stopwords = 'english',
    accept = false
);

CREATE TEXT SEARCH PARSER my_parser (
    START = prsd_start,
    GETTOKEN = prsd_nexttoken,
    END = prsd_end,
    LEXTYPES = prsd_lextype,
    HEADLINE = prsd_headline
);

CREATE TEXT SEARCH TEMPLATE my_template (
    INIT = dsimple_init,
    LEXIZE = dsimple_lexize
);

CREATE TEXT SEARCH TEMPLATE lexize_only (LEXIZE = dsimple_lexize);
