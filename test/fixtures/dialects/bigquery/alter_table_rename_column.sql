ALTER TABLE mydataset.mytable
  RENAME COLUMN A TO columnA,
  RENAME COLUMN IF EXISTS B TO columnB;

ALTER TABLE mydataset.mytable
  RENAME COLUMN columnA TO temp,
  RENAME COLUMN columnB TO columnA,
  RENAME COLUMN temp TO columnB;
