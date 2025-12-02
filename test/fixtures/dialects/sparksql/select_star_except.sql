select * except (col) from table_name where row_no = 1;

select *
except (col)
from table_name where row_no = 1;

select * except (col1, col2, col3, col4, col5) from table_name where row_no = 1;

select a.* except (a.b) from a;
