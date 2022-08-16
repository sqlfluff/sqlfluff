UPDATE t1 SET col1 = col1 + 1;

UPDATE t1 SET col1 = col1 + 1, col2 = col1;

UPDATE items,month SET items.price=month.price
WHERE items.id=month.id;

UPDATE t SET id = id + 1 ORDER BY id DESC;

UPDATE items
SET retail = retail * 0.9
WHERE id IN
(SELECT id FROM items
WHERE retail / wholesale >= 1.3 AND quantity > 100);

UPDATE items,
       (SELECT id FROM items
        WHERE id IN
            (SELECT id FROM items
             WHERE retail / wholesale >= 1.3 AND quantity < 100))
        AS discounted
SET items.retail = items.retail * 0.9
WHERE items.id = discounted.id;

UPDATE items,
       (SELECT id, retail / wholesale AS markup, quantity FROM items)
       AS discounted
    SET items.retail = items.retail * 0.9
    WHERE discounted.markup >= 1.3
    AND discounted.quantity < 100
    AND items.id = discounted.id;

UPDATE LOW_PRIORITY foo
SET bar = 7
LIMIT 4;

UPDATE a, b SET a.name = b.name WHERE a.id = b.id;

UPDATE a join b on a.id = b.id set a.type = b.type where a.type is null;
