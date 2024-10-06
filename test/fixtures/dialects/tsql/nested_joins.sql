SELECT 1 AS RegionCode
FROM BA
LEFT OUTER JOIN I
    LEFT OUTER JOIN P
        ON I.Pcd = P.Iid
    ON BA.Iid = I.Bcd;
GO

SELECT 1
FROM BA
RIGHT OUTER JOIN I
    LEFT OUTER JOIN P AS P_1
        LEFT OUTER JOIN IP AS IP_1
            ON P_1.NID = IP_1.NID
        ON I.PID = CAST(P_1.IDEID AS varchar)
    LEFT OUTER JOIN P AS P_2
        LEFT OUTER JOIN IP AS IP_2
            ON P_2.NID = IP_2.NID
        ON I.SecondaryPID = CAST(P_2.IDEID AS varchar)
    ON CAST(BA.IDEID AS varchar) = I.BAID

SELECT 1 AS RegionCode
FROM BA
LEFT OUTER JOIN (
    I JOIN P
        ON I.Pcd = P.Iid
) ON BA.Iid = I.Bcd;
GO

SELECT
    tst1.Name, tst2.OtherName
FROM dbo.Test1 AS tst1
    LEFT OUTER JOIN (dbo.Test2       AS tst2
                          INNER JOIN dbo.FilterTable AS fltr1
                              ON tst2.Id = fltr1.Id)
        ON tst1.id = tst2.id;
