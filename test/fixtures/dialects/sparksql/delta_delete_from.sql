DELETE FROM events WHERE date < '2017-01-01';

DELETE FROM DELTA.`/data/events/` WHERE date < '2017-01-01';
