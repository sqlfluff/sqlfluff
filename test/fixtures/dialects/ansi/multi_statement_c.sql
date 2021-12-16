select
    *
from boo;
WITH blah AS (select x,y,4.567 FROM foo) select z, y, x from blah;
