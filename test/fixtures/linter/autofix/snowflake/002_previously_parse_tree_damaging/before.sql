merge into foo.bar as tgt
using (
select
  foo::DATE as bar
from foo.bar
where
split(foo, '|')[2] REGEXP '^\\d+\\-\\d+\\-\\d+ \\d+\\:\\d+$'
OR foo IN ('BAR','FOO')
) as src
on
  src.foo = tgt.foo
when matched then
update set
  tgt.foo = src.foo
;
