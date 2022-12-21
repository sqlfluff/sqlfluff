select *
from {{ ref('c') }}
where id = 1
