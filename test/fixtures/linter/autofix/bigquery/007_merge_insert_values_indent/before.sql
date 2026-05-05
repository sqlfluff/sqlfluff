-- VALUES should align with INSERT, not be indented under the column list.
MERGE dataset.detailedinventory AS t
USING dataset.inventory AS s
    ON t.product = s.product
WHEN NOT MATCHED AND quantity < 20 THEN
    INSERT (product, quantity, supply_constrained, comments)
        VALUES (product, quantity, TRUE, 'comment1')
WHEN NOT MATCHED THEN
    INSERT (product, quantity, supply_constrained)
        VALUES (product, quantity, FALSE);
