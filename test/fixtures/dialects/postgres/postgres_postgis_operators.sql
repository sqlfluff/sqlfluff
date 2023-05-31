SELECT tbl1.column1, tbl2.column1, tbl1.column2 && tbl2.column2 AS overlap
FROM ( VALUES
	(1, 'LINESTRING(0 0, 3 3)'::geometry),
	(2, 'LINESTRING(0 1, 0 5)'::geometry)) AS tbl1,
( VALUES
	(3, 'LINESTRING(1 2, 4 6)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 &&& tbl2.column2 AS overlaps_3d,
			            tbl1.column2 && tbl2.column2 AS overlaps_2d
FROM ( VALUES
	(1, 'LINESTRING Z(0 0 1, 3 3 2)'::geometry),
	(2, 'LINESTRING Z(1 2 0, 0 5 -1)'::geometry)) AS tbl1,
( VALUES
	(3, 'LINESTRING Z(1 2 1, 4 6 1)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 &< tbl2.column2 AS overleft
FROM
  ( VALUES
	(1, 'LINESTRING(1 2, 4 6)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING(0 0, 3 3)'::geometry),
	(3, 'LINESTRING(0 1, 0 5)'::geometry),
	(4, 'LINESTRING(6 0, 6 1)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 &<| tbl2.column2 AS overbelow
FROM
  ( VALUES
	(1, 'LINESTRING(6 0, 6 4)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING(0 0, 3 3)'::geometry),
	(3, 'LINESTRING(0 1, 0 5)'::geometry),
	(4, 'LINESTRING(1 2, 4 6)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 &> tbl2.column2 AS overright
FROM
  ( VALUES
	(1, 'LINESTRING(1 2, 4 6)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING(0 0, 3 3)'::geometry),
	(3, 'LINESTRING(0 1, 0 5)'::geometry),
	(4, 'LINESTRING(6 0, 6 1)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 << tbl2.column2 AS strict_left
FROM
  ( VALUES
	(1, 'LINESTRING (1 2, 1 5)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (0 0, 4 3)'::geometry),
	(3, 'LINESTRING (6 0, 6 5)'::geometry),
	(4, 'LINESTRING (2 2, 5 6)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 <<| tbl2.column2 AS below
FROM
  ( VALUES
	(1, 'LINESTRING (0 0, 4 3)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (1 4, 1 7)'::geometry),
	(3, 'LINESTRING (6 1, 6 5)'::geometry),
	(4, 'LINESTRING (2 3, 5 6)'::geometry)) AS tbl2;

SELECT 'LINESTRING(0 0, 0 1, 1 0)'::geometry = 'LINESTRING(1 1, 0 0)'::geometry;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 >> tbl2.column2 AS strict_right
FROM
  ( VALUES
	(1, 'LINESTRING (2 3, 5 6)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (1 4, 1 7)'::geometry),
	(3, 'LINESTRING (6 1, 6 5)'::geometry),
	(4, 'LINESTRING (0 0, 4 3)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 @ tbl2.column2 AS contained
FROM
  ( VALUES
	(1, 'LINESTRING (1 1, 3 3)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (0 0, 4 4)'::geometry),
	(3, 'LINESTRING (2 2, 4 4)'::geometry),
	(4, 'LINESTRING (1 1, 3 3)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 |&> tbl2.column2 AS overabove
FROM
  ( VALUES
	(1, 'LINESTRING(6 0, 6 4)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING(0 0, 3 3)'::geometry),
	(3, 'LINESTRING(0 1, 0 5)'::geometry),
	(4, 'LINESTRING(1 2, 4 6)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 |>> tbl2.column2 AS above
FROM
  ( VALUES
	(1, 'LINESTRING (1 4, 1 7)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (0 0, 4 2)'::geometry),
	(3, 'LINESTRING (6 1, 6 5)'::geometry),
	(4, 'LINESTRING (2 3, 5 6)'::geometry)) AS tbl2;

SELECT tbl1.column1, tbl2.column1, tbl1.column2 ~ tbl2.column2 AS contains
FROM
  ( VALUES
	(1, 'LINESTRING (0 0, 3 3)'::geometry)) AS tbl1,
  ( VALUES
	(2, 'LINESTRING (0 0, 4 4)'::geometry),
	(3, 'LINESTRING (1 1, 2 2)'::geometry),
	(4, 'LINESTRING (0 0, 3 3)'::geometry)) AS tbl2;

select 'LINESTRING(0 0, 1 1)'::geometry ~= 'LINESTRING(0 1, 1 0)'::geometry as equality;

SELECT st_distance(geom, 'SRID=3005;POINT(1011102 450541)'::geometry) as d,edabbr, vaabbr
FROM va2005
ORDER BY geom <-> 'SRID=3005;POINT(1011102 450541)'::geometry limit 10;

SELECT track_id, dist FROM (
  SELECT track_id, ST_DistanceCPA(tr,:qt) dist
  FROM trajectories
  ORDER BY tr |=| :qt
  LIMIT 5
) foo;

SELECT *
FROM (
SELECT b.tlid, b.mtfcc,
	b.geom <#> ST_GeomFromText('LINESTRING(746149 2948672,745954 2948576,
		745787 2948499,745740 2948468,745712 2948438,
		745690 2948384,745677 2948319)',2249) As b_dist,
		ST_Distance(b.geom, ST_GeomFromText('LINESTRING(746149 2948672,745954 2948576,
		745787 2948499,745740 2948468,745712 2948438,
		745690 2948384,745677 2948319)',2249)) As act_dist
    FROM bos_roads As b
    ORDER BY b_dist, b.tlid
    LIMIT 100) As foo
    ORDER BY act_dist, tlid LIMIT 10;

WITH index_query AS (
  SELECT ST_Distance(geom, 'SRID=3005;POINT(1011102 450541)'::geometry) as d,edabbr, vaabbr
	FROM va2005
  ORDER BY geom <<->> 'SRID=3005;POINT(1011102 450541)'::geometry LIMIT 100)
  SELECT *
	FROM index_query
  ORDER BY d limit 10;

WITH index_query AS (
  SELECT ST_Distance(geom, 'SRID=3005;POINT(1011102 450541)'::geometry) as d,edabbr, vaabbr
	FROM va2005
  ORDER BY geom <<#>> 'SRID=3005;POINT(1011102 450541)'::geometry LIMIT 100)
  SELECT *
	FROM index_query
  ORDER BY d limit 10;
