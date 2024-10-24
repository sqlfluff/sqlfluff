SELECT
    FIRST_VALUE(
        [entrypunt]) IGNORE NULLS
    OVER
    (
        PARTITION BY ([reisnummer])
        ORDER BY [reismutatie starttijdstip]
    ) AS [entrypunt]
FROM [reizen]
