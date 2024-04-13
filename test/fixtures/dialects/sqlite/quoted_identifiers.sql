SELECT `nih`.`userID`
FROM `flight_notification_item_history` AS `nih`;

-- NOTE: Normally single quoted items are interpreted as strings rather than objects - but this does still run on SQLite.
SELECT 'nih'.'userID'
FROM 'flight_notification_item_history' AS 'nih';

SELECT "nih"."userID"
FROM "flight_notification_item_history" AS "nih";
