SELECT * FROM my_table AT ( TIMESTAMP => '2024-06-05 12:30:00'::TIMESTAMP_LTZ );

SELECT * FROM my_table AT ( TIMESTAMP => '2024-06-05 12:30:00'::TIMESTAMP );

SELECT * FROM my_table AT ( TIMESTAMP => '2024-06-05 12:30:00' );

SELECT * FROM my_table AT ( TIMESTAMP => '2024-06-05 12:30:00' ) AS T;

SELECT * FROM my_table BEFORE(STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');

SELECT oldt.* ,newt.*
   FROM my_table BEFORE(STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726') AS oldt
     FULL OUTER JOIN my_table AT(STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726') AS newt
     ON oldt.id = newt.id
   WHERE oldt.id IS NULL OR newt.id IS NULL;

 SELECT *
   FROM db1.public.htt1
     AT(TIMESTAMP => '2024-06-05 17:50:00'::TIMESTAMP_LTZ) h
     JOIN db1.public.tt1
     AT(TIMESTAMP => '2024-06-05 17:50:00'::TIMESTAMP_LTZ) t
     ON h.c1=t.c1;


-- https://github.com/sqlfluff/sqlfluff/issues/6070
SELECT * FROM my_table AT (TIMESTAMP => TO_TIMESTAMP(DATEADD('DAY', -1, DATEADD('MONTH', -1, DATEADD('DAY', -1, CURRENT_DATE)))));

-- https://github.com/sqlfluff/sqlfluff/issues/5570
SELECT * FROM my_table AT(TIMESTAMP => 'Fri, 01 May 2015 16:20:00 -0700'::timestamp_tz);
