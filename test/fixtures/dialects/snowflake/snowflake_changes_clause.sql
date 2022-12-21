select *
from t1
  changes(information => default)
  at(timestamp => 'Fri, 01 May 2015 16:20:00 -0700'::timestamp);

select *
from t1
  changes(information => append_only)
  at(offset => -60*5);

select c1
from t1
  changes(information => append_only)
  at(timestamp => 'Fri, 01 May 2015 16:20:00 -0700'::timestamp)
  end(timestamp => 'Fri, 05 May 2015 16:20:00 -0700'::timestamp);

select *
from t1
  changes(information => default)
  before(statement => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');
