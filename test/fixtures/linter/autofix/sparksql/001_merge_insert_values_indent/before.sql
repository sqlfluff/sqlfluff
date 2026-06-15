-- VALUES should align with INSERT, not be indented under the column list.
MERGE INTO dataset.detailedinventory AS t
USING dataset.inventory AS s
    ON t.product = s.product
WHEN NOT MATCHED AND quantity < 20 THEN
    INSERT (product, quantity, supply_constrained)
        VALUES (product, quantity, TRUE)
WHEN NOT MATCHED THEN
    INSERT (product, quantity, supply_constrained)
        VALUES (product, quantity, FALSE);
