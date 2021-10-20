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
	,[Date]
