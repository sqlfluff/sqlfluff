IMPORT FOREIGN SCHEMA foreign_films
    FROM SERVER film_server INTO films;

IMPORT FOREIGN SCHEMA "TEST"
    FROM SERVER test_server INTO test;

IMPORT FOREIGN SCHEMA foreign_films LIMIT TO (actors, directors)
    FROM SERVER film_server INTO films;
