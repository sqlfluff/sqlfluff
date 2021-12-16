-- On clause without brackets
-- https://github.com/sqlfluff/sqlfluff/issues/146
SELECT
    a
FROM
    zendesk
LEFT JOIN
    ticket
ON
    zendesk.ticket_id = ticket.id;

SELECT
    low_user_counts
FROM
    acceptable_buckets
JOIN
    small_buckets
ON
    (business_type = low_business_type)
    AND (business_type = low_business_type
        OR size_label = low_size_label);
