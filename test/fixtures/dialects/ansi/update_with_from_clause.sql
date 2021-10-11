UPDATE
  my_table
SET
  my_table.days=other_table.days
FROM
  other_table
WHERE
  my_table.po_number=other_table.po_number
