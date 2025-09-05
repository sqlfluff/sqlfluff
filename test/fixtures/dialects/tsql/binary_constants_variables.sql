-- T-SQL binary constants variable assignment test cases
-- Variable assignment with binary constants
declare @var1 binary(1);
set @var1 = 0x0;

declare @var2 binary(2);
set @var2 = 0xAE;

declare @var3 binary(8);
set @var3 = 0x69048AEFDD010E;

-- Empty binary constant
declare @var4 binary(16);
set @var4 = 0x;
