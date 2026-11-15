-- `#` is the bitwise XOR of integers and bit strings.
SELECT 5 # 3;

SELECT B'10101' # B'01110';

SELECT flags # 4 AS toggled
FROM settings
WHERE (flags # mask) & 1 = 1;

SELECT 5#3;

-- It's also the point where two geometric objects intersect.
SELECT lseg '[(0,0),(2,2)]' # lseg '[(0,2),(2,0)]';

-- `##` is the point on the second object closest to the first.
SELECT point '(1,2)' ## lseg '[(0,0),(2,0)]';

SELECT 5 OPERATOR(pg_catalog.#) 3;

-- The JSON operators that start with `#` are still one operator each.
SELECT data #> '{a,b}', data #>> '{a,b}', data #- '{a}'
FROM documents;
