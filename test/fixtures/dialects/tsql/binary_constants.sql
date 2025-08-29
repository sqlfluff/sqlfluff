-- T-SQL binary constants test cases
-- Test basic binary constants parsing
select 0x0;
select 0xAE;
select 0x12Ef;
select 0x69048AEFDD010E;
select 0x;

-- Test mixed case
select 0X0;
select 0XAE;

-- Test multiple constants in one query  
select 0x0, 0xAE, 0x12Ef;

-- Test with old-style x'...' format
select x'FF', X'DEAD';
