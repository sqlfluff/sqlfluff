ALTER TABLE mydataset.mytable
  ADD COLUMN A STRING,
  ADD COLUMN IF NOT EXISTS B GEOGRAPHY,
  ADD COLUMN C ARRAY<NUMERIC>,
  ADD COLUMN D DATE OPTIONS(description="my description");

ALTER TABLE mydataset.mytable
   ADD COLUMN A STRUCT<
       B GEOGRAPHY,
       C ARRAY<INT64>,
       D INT64 NOT NULL,
       E TIMESTAMP OPTIONS(description="creation time")
       >;
