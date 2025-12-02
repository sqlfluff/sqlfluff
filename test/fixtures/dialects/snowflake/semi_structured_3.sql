SELECT
    PARSE_JSON(t.metadata)['names'][0] AS first_name,
    PARSE_JSON(t.metadata):customer_id AS customer_id
FROM tickets AS t
