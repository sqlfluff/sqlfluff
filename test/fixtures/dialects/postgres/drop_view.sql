DROP VIEW abc;

DROP VIEW "abc";

DROP VIEW IF EXISTS abc;

DROP VIEW abc, "def", ghi;

DROP VIEW IF EXISTS abc, def, ghi;

-- Test CASCADE trailing keyword

DROP VIEW abc CASCADE;

DROP VIEW IF EXISTS abc CASCADE;

DROP VIEW abc, def, ghi CASCADE;

DROP VIEW IF EXISTS abc, def, ghi CASCADE;


-- Test RESTRICT trailing keyword

DROP VIEW abc RESTRICT;

DROP VIEW IF EXISTS abc RESTRICT;

DROP VIEW abc, def, ghi RESTRICT;

DROP VIEW IF EXISTS abc, def, ghi RESTRICT;
