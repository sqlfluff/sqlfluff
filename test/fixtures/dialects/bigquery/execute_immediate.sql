declare var_1 string;
declare var_2 string;

set var_1 = '''
insert into project.data_set.table
select
  "%s" as var_1,
  count(*) as column_1
from (
  select column_3
  from %s.column_2
  group by var_3 having count(var_3) > 1
)
''';

create or replace table project.data_set.table (var_1 string, column_1 int64)
options (
    expiration_timestamp = timestamp_add(current_timestamp(), interval 3 hour)
);

for m in (select var_1 from project.data_set.table) do
    set var_1 = m[0];
    execute immediate 'select 1;';
    execute immediate var_1;
    execute immediate format(var_2, var_1, var_1);
    execute immediate case
        when x then format(var_1, var_2) else format(var_1, m)
    end;
    execute immediate (select format(var_2, var_1, var_1));
    execute immediate 'SELECT 2 + 3' into y;
    execute immediate 'SELECT 2 + 3, 6' into y, z;
    execute immediate 'SELECT ? * (? + 2)' into y using 1, 3;
    execute immediate 'SELECT @a * (@b + 2)' into y using 1 as a, x as b;
end for;
