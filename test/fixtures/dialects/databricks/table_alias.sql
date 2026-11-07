-- KEYS, PIVOT and WINDOW are not reserved as aliases, so they are legal
-- unquoted column and table aliases with an explicit AS.
select a as keys from t;
select a as pivot from t;
select a as window from t;
select * from t as keys;
select * from t as pivot;
select * from t as window;
