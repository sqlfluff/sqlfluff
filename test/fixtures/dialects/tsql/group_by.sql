CREATE TABLE #n 
WITH (DISTRIBUTION = ROUND_ROBIN)
AS 
( Select acto.ActionDTS
  FROM Orders_Action acto
)

SELECT 
      t.actiondts
FROM #n t
GROUP BY    t.ActionDTS;

DROP  TABLE #n;
