ALTER TABLE mydataset.mytable
SET OPTIONS (
  expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY),
  description="Table that expires seven days from now"
);

ALTER TABLE table
SET OPTIONS (expiration_timestamp = NULL)
;
