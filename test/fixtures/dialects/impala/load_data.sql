LOAD DATA INPATH '/user/data/incoming' OVERWRITE INTO TABLE db.t1
  PARTITION (year=2024, month=1);
