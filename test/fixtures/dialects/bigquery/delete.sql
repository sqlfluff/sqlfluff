DELETE dataset.Inventory
WHERE quantity = 0;

DELETE dataset.Inventory i
WHERE i.product NOT IN (SELECT product from dataset.NewArrivals);

DELETE dataset.Inventory
WHERE NOT EXISTS
  (SELECT * from dataset.NewArrivals
   WHERE Inventory.product = NewArrivals.product);
