-- Test no trailing keyword with combinations of:
--  * IF EXISTS
--  * One publication vs multiple publications.

DROP PUBLICATION abc;

DROP PUBLICATION "abc";

DROP PUBLICATION IF EXISTS abc;

DROP PUBLICATION abc, "def", ghi;

DROP PUBLICATION IF EXISTS abc, def, ghi;

-- Test CASCADE trailing keyword

DROP PUBLICATION abc CASCADE;

DROP PUBLICATION IF EXISTS abc CASCADE;

DROP PUBLICATION abc, def, ghi CASCADE;

DROP PUBLICATION IF EXISTS abc, def, ghi CASCADE;


-- Test RESTRICT trailing keyword

DROP PUBLICATION abc RESTRICT;

DROP PUBLICATION IF EXISTS abc RESTRICT;

DROP PUBLICATION abc, def, ghi RESTRICT;

DROP PUBLICATION IF EXISTS abc, def, ghi RESTRICT;
