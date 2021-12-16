DELETE dbo.Table2   
FROM dbo.Table2   
    INNER JOIN dbo.Table1   
    ON (dbo.Table2.ColA = dbo.Table1.ColA)
    WHERE dboTable2.ColA = 1; 
