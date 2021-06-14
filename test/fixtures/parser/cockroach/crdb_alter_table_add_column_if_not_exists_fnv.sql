ALTER TABLE t1 ADD COLUMN IF NOT EXISTS x int8 AS (fnv32(a::string, b::string, c::string)%8) stored CHECK (x IN (0, 1, 2, 3, 4, 5, 6, 7));
