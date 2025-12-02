create stream new_stream on table table_name;

create stream mystream on table mytable before (timestamp => to_timestamp(40*365*86400));

create stream mystream on table mytable at(offset => -60*5);

create stream mystream on table mytable before(statement => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');

create stream new_stream on external table table_name;

create stream new_stream on stage stage_name;

create stream new_stream on view view_name;

create stream new_stream clone source_stream;

create or replace stream new_stream on table table_name;

create stream if not exists new_stream on table table_name;
CREATE OR REPLACE STREAM new_stream
COPY GRANTS
ON TABLE table_name
APPEND_ONLY = TRUE
SHOW_INITIAL_ROWS = TRUE
COMMENT = 'amazing comment';

CREATE OR REPLACE STREAM new_stream
ON EXTERNAL TABLE table_name
INSERT_ONLY = TRUE
COMMENT = 'amazing comment';

CREATE STREAM IF NOT EXISTS new_stream
ON STAGE stage_name
COMMENT = 'amazing comment';

CREATE STREAM IF NOT EXISTS new_stream
ON VIEW view_name
APPEND_ONLY = FALSE
SHOW_INITIAL_ROWS = FALSE
COMMENT = 'amazing comment';
