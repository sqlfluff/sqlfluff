SELECT
  t.$1, t.$2
FROM @mystage1 (file_format => myformat) t
;

select t.$1, t.$2 from @mystage1 (file_format => 'myformat', pattern=>'.*data.*[.]csv.gz') t;

select t.$1, t.$2 from @mystage1 (pattern=>'.*data.*[.]csv.gz', file_format => 'myformat') t;

select t.$1, t.$2 from @mystage1 (pattern=>'.*data.*[.]csv.gz') t;

select t.$1, t.$2 from @mystage1 t;
