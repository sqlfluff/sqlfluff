SELECT
	house_id,
	COUNT (person_id)
FROM
	persons
GROUP BY
	house_id
HAVING
	COUNT (person_id) > 10
FETCH FIRST 30 ROWS ONLY
