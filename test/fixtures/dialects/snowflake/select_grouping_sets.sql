SELECT foo, bar FROM baz GROUP BY GROUPING SETS (foo, bar);

select count(*), medical_license, radio_license
  from nurses
  group by grouping sets (medical_license, radio_license);

select count(*), medical_license, radio_license
  from nurses
  group by grouping sets (medical_license, radio_license);
