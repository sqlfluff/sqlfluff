ALTER VIEW mydataset.myview
SET OPTIONS (
  expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY),
  description="View that expires seven days from now"
);
