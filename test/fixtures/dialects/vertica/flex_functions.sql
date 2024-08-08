select
    applicant_verification_id,
    etl_created_at,
    etl_updated_at,
    mapkeys(some_data)
        over (
            partition by
                col_1,
                col2
        )
    as (
        json_table_keys
    )
from json_table
