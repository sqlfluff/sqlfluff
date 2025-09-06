CREATE TEXT SEARCH CONFIGURATION my_config (
    PARSER = my_parser
);
CREATE TEXT SEARCH CONFIGURATION public.my_config (
    PARSER = pg_catalog."default"
);
CREATE TEXT SEARCH CONFIGURATION copy_config (
    COPY = pg_catalog.english
);
