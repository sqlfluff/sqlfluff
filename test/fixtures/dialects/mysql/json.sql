CREATE TABLE facts (sentence JSON);

INSERT INTO facts VALUES
(JSON_OBJECT("mascot", "Our mascot is a dolphin named \"Sakila\"."));

SELECT sentence->"$.mascot" FROM facts;

SELECT sentence->'$.mascot' FROM facts;

SELECT sentence->>"$.mascot" FROM facts;

SELECT sentence->>'$.mascot' FROM facts;

SELECT sentence FROM facts WHERE JSON_TYPE(sentence->"$.mascot") = "NULL";

SELECT sentence FROM facts WHERE sentence->"$.mascot" IS NULL;
