SELECT
    id,
    name,
    age,
    class,
    address,
    c_age,
    d_age
FROM person
    LATERAL VIEW EXPLODE(ARRAY(30, 60)) tbl_name AS c_age
    LATERAL VIEW EXPLODE(ARRAY(40, 80)) AS d_age;

SELECT
    c_age,
    COUNT(*) AS record_count
FROM person
    LATERAL VIEW EXPLODE(ARRAY(30, 60)) AS c_age
    LATERAL VIEW EXPLODE(ARRAY(40, 80)) AS d_age
GROUP BY c_age;

SELECT
    id,
    name,
    age,
    class,
    address,
    c_age,
    d_age
FROM person
    LATERAL VIEW EXPLODE(ARRAY()) tbl_name AS c_age;

SELECT
    id,
    name,
    age,
    class,
    address,
    time,
    c_age
FROM person
    LATERAL VIEW OUTER EXPLODE(ARRAY()) tbl_name AS c_age;

SELECT
    id,
    name,
    age,
    class,
    address,
    time,
    c_age
FROM person
    LATERAL VIEW OUTER EXPLODE(ARRAY()) tbl_name c_age;

SELECT
    id,
    name,
    age,
    class,
    address,
    time,
    c_age
FROM person
    LATERAL VIEW OUTER EXPLODE(ARRAY()) c_age;

SELECT
    person.id,
    exploded_people.name,
    exploded_people.age,
    exploded_people.state
FROM person
    LATERAL VIEW INLINE(array_of_structs) exploded_people AS name, age, state;

SELECT
    p.id,
    exploded_people.name,
    exploded_people.age,
    exploded_people.state
FROM person AS p
    LATERAL VIEW INLINE(array_of_structs) exploded_people AS name, age, state;

SELECT
    p.id,
    exploded_people.name,
    exploded_people.age,
    exploded_people.state
FROM person AS p
    LATERAL VIEW INLINE(array_of_structs) exploded_people;

SELECT
    p.id,
    exploded_people.name,
    exploded_people.age,
    exploded_people.state
FROM person AS p
    LATERAL VIEW INLINE(array_of_structs) exploded_people name, age, state;

SELECT
    p.id,
    exploded_people.name,
    exploded_people.age,
    exploded_people.state
FROM person AS p
    LATERAL VIEW INLINE(array_of_structs) AS name, age, state;

SELECT
    t1.column1,
    CAST(GET_JSON_OBJECT(things, '$.percentage') AS DECIMAL(16, 8)
    ) AS ptc
FROM table1 AS t1
LEFT JOIN table2 AS t2
    ON
        c.column1 = p.column1
        AND t2.type = 'SOMETHING'
    LATERAL VIEW OUTER EXPLODE(t2.column2) AS things;
