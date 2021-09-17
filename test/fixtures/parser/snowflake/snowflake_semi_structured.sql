-- tests parsing of table functions and semi structured accessing.
SELECT
    ticket_id,
    value:value AS uncasted,
    value:id::bigint AS field_id,
    value:value::STRING AS field_val,
    value:thing[4].foo AS another_val,
    value:thing[4].bar.baz[0].foo::bigint AS another_val
FROM raw_tickets, lateral flatten(INPUT => custom_fields)
