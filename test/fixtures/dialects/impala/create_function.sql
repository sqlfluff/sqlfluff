CREATE FUNCTION db.my_func(INT) RETURNS INT
  LOCATION '/user/udf/my_func.so'
  SYMBOL='my_func_symbol';

CREATE AGGREGATE FUNCTION db.my_agg(INT) RETURNS DOUBLE
  INTERMEDIATE STRING
  LOCATION '/user/udf/my_agg.so'
  INIT_FN='init'
  UPDATE_FN='update'
  MERGE_FN='merge';
