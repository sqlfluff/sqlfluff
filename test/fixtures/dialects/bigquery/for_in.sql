
-- For statment
FOR record IN
  (SELECT word, word_count
   FROM bigquery-public-data.samples.shakespeare
   LIMIT 5)
DO
  SELECT record.word, record.word_count;
END FOR;

-- Multiple statements
FOR record IN
  (SELECT word, word_count
   FROM bigquery-public-data.samples.shakespeare
   LIMIT 5)
DO
  SELECT record.word, record.word_count;
  SELECT record.word, record.word_count;
  SELECT record.word, record.word_count;
END FOR;

-- With Assert
FOR user IN (
    SELECT
        group1,
	    count(*) as count
    FROM `database.user`
)
DO
	ASSERT (COUNT > 0);
END FOR;
