SELECT
    DATE(zendesk.created_at, 'America/New_York') AS date,
    COUNT(
        CASE
        WHEN zendesk.support_team IN ('tech support', 'taskus', 'onc') THEN 1
        END
    ) AS tech_support
FROM
    zendesk
