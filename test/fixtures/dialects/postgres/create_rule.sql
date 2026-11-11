CREATE RULE protect_orders AS ON DELETE TO orders DO INSTEAD NOTHING;

CREATE OR REPLACE RULE notify_orders AS ON UPDATE TO orders DO ALSO NOTIFY orders_changed;

CREATE RULE log_order_insert AS ON INSERT TO orders
    DO INSERT INTO order_log VALUES (NEW.id, 'inserted');

CREATE RULE archive_order AS ON DELETE TO sales.orders
    WHERE OLD.status = 'closed'
    DO ALSO (
        INSERT INTO order_log VALUES (OLD.id, 'archived');
        UPDATE order_totals SET n = n - 1 WHERE customer_id = OLD.customer_id
    );

CREATE RULE notify_order_insert AS ON INSERT TO sales.orders
    DO ALSO (; NOTIFY orders_changed;; NOTIFY order_inserted, 'new';);

CREATE RULE ignore_insert AS ON INSERT TO order_totals DO INSTEAD ();

CREATE RULE select_on_update AS ON UPDATE TO order_totals DO ALSO ((SELECT 1));

CREATE RULE log_order_delete AS ON DELETE TO order_totals
    DO ALSO WITH note AS (SELECT 'deleted' AS txt)
    INSERT INTO order_log SELECT OLD.customer_id, txt FROM note;

CREATE RULE soft_delete AS ON DELETE TO customers
    DO INSTEAD UPDATE customers SET deleted = TRUE WHERE id = OLD.id RETURNING *;

CREATE OR REPLACE RULE "_RETURN" AS ON SELECT TO order_view DO INSTEAD SELECT 2 AS a;
