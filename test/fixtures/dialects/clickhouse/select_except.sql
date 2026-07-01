SELECT * EXCEPT (c1) from t1;
SELECT * EXCEPT (c1, c2) from t1;
SELECT * EXCEPT c1 from t1;
SELECT t1.* EXCEPT c1 from t1;
