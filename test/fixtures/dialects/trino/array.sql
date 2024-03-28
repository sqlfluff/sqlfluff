SELECT ARRAY[1,2] || ARRAY[3,4];

SELECT ARRAY[ARRAY['meeting', 'lunch'], ARRAY['training', 'presentation']];

SELECT column FROM UNNEST(ARRAY[1, 2]);

SELECT FILTER(ARRAY[5, -6, NULL, 7], x -> x > 0);

SELECT ANY_MATCH(ARRAY[5, -6, NULL, 7], x -> x > 0);

SELECT ELEMENT_AT(ARRAY['apple', 'banana', 'orange'], 2);
