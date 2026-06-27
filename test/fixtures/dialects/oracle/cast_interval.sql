select cast(type_char as interval year to month) as val from sample_types where id = 1;
select cast(type_char as interval year(9) to month) as val from sample_types where id = 1;
select cast(type_char as interval day to second) as val from sample_types where id = 1;
select cast(type_char as interval day(2) to second(6)) as val from sample_types where id = 1;
