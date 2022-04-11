DELETE FROM events WHERE date < '2017-01-01';

DELETE FROM DELTA.`/data/events/` WHERE date < '2017-01-01';

DELETE FROM all_events
WHERE session_time < (
    SELECT min(session_time)
    FROM good_events
);

DELETE FROM orders AS t1
WHERE EXISTS (
    SELECT returned_orders.oid
    FROM returned_orders
    WHERE t1.oid = returned_orders.oid
);

DELETE FROM events
WHERE category NOT IN (
    SELECT category
    FROM events2
    WHERE date > '2001-01-01'
);
