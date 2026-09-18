-- get the full history of the table
DESCRIBE HISTORY '/data/events/';

DESCRIBE HISTORY DELTA.`/data/events/`;

-- get the last operation only
DESCRIBE HISTORY '/data/events/' LIMIT 1;

DESCRIBE HISTORY EVENTSTABLE;

-- DESC is accepted wherever DESCRIBE is
DESC HISTORY EVENTSTABLE;

DESC HISTORY '/data/events/' LIMIT 1;

DESC HISTORY DELTA.`/data/events/`;
