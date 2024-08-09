SELECT col1
FROM {{ ref('other_project', 'my_table') }}
