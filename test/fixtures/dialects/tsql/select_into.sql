SELECT [ID]
	,[FIN]
	,[Unit]
	,[EventNM]
	,[Date]
	,[CHGFlag]
INTO #CHG
FROM Final
GROUP BY [FIN]
	,[EventNM]
	,[Unit]
	,[Date];

SELECT name, identity(int, -1, -1) ID
INTO #temp
FROM sys.objects;
