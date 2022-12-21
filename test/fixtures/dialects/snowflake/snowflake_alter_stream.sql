alter stream mystream set comment = 'New comment for stream';

alter stream if exists mystream set tag mytag='myvalue';

ALTER STREAM IF EXISTS mystream SET
APPEND_ONLY = FALSE
TAG mytag1='myvalue1', mytag2 = 'myvalue2'
COMMENT = 'amazing comment';

ALTER STREAM IF EXISTS mystream SET
INSERT_ONLY = TRUE
COMMENT = 'amazing comment';

alter stream mystream unset comment;

alter stream mystream unset tag mytag1, mytag2;
