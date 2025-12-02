UPDATE events SET event_type = 'click' WHERE event_type = 'clck';

UPDATE DELTA.`/data/events/` SET event_type = 'click' WHERE event_type = 'clck';

UPDATE all_events
SET session_time = 0, ignored = true
WHERE session_time < (
    SELECT min(session_time)
    FROM good_events
);

UPDATE orders AS t1
SET order_status = 'returned'
WHERE EXISTS (
    SELECT returned_orders.oid
    FROM returned_orders
    WHERE t1.oid = returned_orders.oid
);

UPDATE events
SET category = 'undefined'
WHERE category NOT IN (
    SELECT category
    FROM events2
    WHERE date > '2001-01-01'
);
