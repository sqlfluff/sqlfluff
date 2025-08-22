"""T-SQL binary constants function calls test cases."""
-- Function calls with binary constants
select CAST(0x0 as uniqueidentifier);
select CAST(0xAE as binary(2));
select CAST(0x12Ef as varbinary(16));

-- Mixed cases with functions
select CAST(0X0 as uniqueidentifier);
select CONVERT(binary(4), 0x69048AEF);

-- Empty binary constant in function
select CAST(0x as binary(1));