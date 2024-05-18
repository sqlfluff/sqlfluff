select 1
from {{ source('jaffle_shop', 'orders') }}
