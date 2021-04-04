SELECT
       onetable.f1,
       twotable.f1
FROM onetable
         LEFT JOIN
     twotable
         FORCE INDEX FOR JOIN (idx_index)
     ON onetable.f1 = twotable.f1