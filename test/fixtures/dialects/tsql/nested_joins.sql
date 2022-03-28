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
