select
    id,
    name{% if false %}, secret_column_number_one, secret_column_number_two, abc{% endif %}
from customers
