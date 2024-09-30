SELECT
    client.reference,
    client.name
FROM client
GROUP BY client.reference, client.name
ORDER BY client.reference
OFFSET 10 ROWS;

SELECT
    client.reference,
    client.name
FROM client
GROUP BY client.reference, client.name
ORDER BY client.reference
OFFSET 10 ROWS
FETCH NEXT 10 ROWS ONLY;
