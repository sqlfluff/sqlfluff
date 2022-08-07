-- get the full history of the table
DESCRIBE HISTORY '/data/events/';

DESCRIBE HISTORY DELTA.`/data/events/`;

-- get the last operation only
DESCRIBE HISTORY '/data/events/' LIMIT 1;

DESCRIBE HISTORY EVENTSTABLE;
