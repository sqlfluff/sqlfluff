select first_value(finalsaleprice ignore nulls) over () as c1
from table1
