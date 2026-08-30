create or replace view example as
select smthng
from smwhr
/

comment on table example is 'abc'
/

create or replace public synonym example for example
/

-- A bare `/` mid-line is division, not the buffer executor
create or replace view example_division as
select 1 / 100 as z, nvl(bytes, 0) / 1024 / 1024 as size_mb
from smwhr
where sample_time > sysdate - 1/24
/
