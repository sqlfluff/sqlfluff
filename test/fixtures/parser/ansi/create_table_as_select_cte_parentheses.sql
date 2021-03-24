CREATE TABLE final_rows AS
(
    WITH source_table AS
    (
        SELECT * FROM source_data
    )
    SELECT * FROM source_table
)
