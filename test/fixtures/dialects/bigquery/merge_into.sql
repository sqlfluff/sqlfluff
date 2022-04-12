MERGE dataset.detailedinventory t
USING dataset.inventory s
ON t.product = s.product
WHEN NOT MATCHED AND quantity < 20 THEN
    INSERT(product, quantity, supply_constrained, comments)
        VALUES(product, quantity, TRUE)
WHEN NOT MATCHED THEN
    INSERT(product, quantity, supply_constrained)
        VALUES(product, quantity, FALSE);

MERGE dataset.inventory t
USING dataset.newarrivals s
ON t.product = s.product
WHEN MATCHED THEN
    UPDATE SET quantity = t.quantity + s.quantity
WHEN NOT MATCHED THEN
    INSERT (product, quantity) VALUES(product, quantity);

MERGE dataset.newarrivals t
USING (SELECT * FROM dataset.newarrivals WHERE warehouse != 'warehouse #2') s
ON t.product = s.product
WHEN MATCHED AND t.warehouse = 'warehouse #1' THEN
    UPDATE SET quantity = t.quantity + 20
WHEN MATCHED THEN
    DELETE;

MERGE dataset.inventory t
USING
    (SELECT
        product,
        quantity,
        state
        FROM dataset.newarrivals INNER JOIN dataset.warehouse ON dataset.newarrivals.warehouse = dataset.warehouse.warehouse) s
ON t.product = s.product
WHEN MATCHED AND state = 'CA' THEN
    UPDATE SET quantity = t.quantity + s.quantity
WHEN MATCHED THEN
    DELETE;

MERGE dataset.inventory t
USING dataset.newarrivals s
ON t.product = s.product
WHEN MATCHED THEN
    UPDATE SET quantity = t.quantity + s.quantity;
