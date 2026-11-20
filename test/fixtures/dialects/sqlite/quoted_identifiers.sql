SELECT `nih`.`userID`
FROM `flight_notification_item_history` AS `nih`;

-- NOTE: Normally single quoted items are interpreted as strings rather than objects - but this does still run on SQLite.
SELECT 'nih'.'userID'
FROM 'flight_notification_item_history' AS 'nih';

SELECT "nih"."userID"
FROM "flight_notification_item_history" AS "nih";

SELECT [nih].[userID], [nih].[user name] AS [name]
FROM [flight_notification_item_history] AS [nih];

CREATE TABLE [order items] ([item id] INTEGER PRIMARY KEY, [select] TEXT);

CREATE INDEX [idx "x"] ON [order items] ([select]);
