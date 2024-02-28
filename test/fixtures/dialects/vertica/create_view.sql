CREATE VIEW temp_t0 AS SELECT * from t0_p1 UNION ALL
     SELECT * from t0_p2 UNION ALL
       SELECT * from t0_p3 UNION ALL
         SELECT * from t0_p4 UNION ALL
           SELECT * from t0_p5;
