-- columns expression with lambda
SELECT COLUMNS(c -> c LIKE '%num%') FROM addresses;

-- columns expression with regular expression
SELECT COLUMNS('number\d+') FROM addresses;

-- function call on columns expression
SELECT min(COLUMNS(*)) FROM addresses;

SELECT min(COLUMNS(*)), count(COLUMNS(*)) FROM numbers;

-- columns with wildcard replace and exclude
SELECT min(COLUMNS(* REPLACE (number + id AS number))), count(COLUMNS(* EXCLUDE (number))) FROM numbers;

-- columns expression with an expression
SELECT COLUMNS(*) + COLUMNS(*) FROM numbers;
