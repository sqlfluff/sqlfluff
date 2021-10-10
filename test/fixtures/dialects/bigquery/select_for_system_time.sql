SELECT
    user_id
FROM
    lists_emails AS list_emails
    FOR SYSTEM_TIME AS OF CAST('2019-12-02T20:52:34+00:00' AS TIMESTAMP)