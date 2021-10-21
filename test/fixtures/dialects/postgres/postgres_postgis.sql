CREATE TABLE public.foo
(
    quadkey TEXT,
    my_geometry_column GEOMETRY (GEOMETRY, 4326),
    my_point POINT(0 0),
    my_linestring LINESTRING(0 0, 1 1, 2 1, 2 2),
    my_simple_polygon POLYGON((0 0, 1 0, 1 1, 0 1, 0 0)),
    my_complex_polygon POLYGON((0 0, 10 0, 10 10, 0 10, 0 0),(1 1, 1 2, 2 2, 2 1, 1 1)),
    my_geometry_collection GEOMETRYCOLLECTION(POINT(2 0),POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))),
    my_3d_linestring LINESTRINGZ (0 0 0,1 0 0,1 1 2),
    my_geography_column GEOGRAPHY(GEOGRAPHY, 6679),
    my_4d_point POINTZM(1, 1, 1, 1),
    my_multicurve MULTICURVE( (0 0, 5 5), CIRCULARSTRING(4 0, 4 4, 8 4) ),
    my_tin TIN( ((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)) ),
    my_triangle TRIANGLE ((0 0, 0 9, 9 0, 0 0)),
    my_polyhedral_surface POLYHEDRALSURFACE( ((0 0 0, 0 0 1, 0 1 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 1 0 0, 0 0 0)), ((0 0 0, 1 0 0, 1 0 1, 0 0 1, 0
0 0)), ((1 1 0, 1 1 1, 1 0 1, 1 0 0, 1 1 0)), ((0 1 0, 0 1 1, 1 1 1, 1 1 0, 0 1 0)), ((0 0 1, 1 0 1, 1 1 1, 0 1 1, 0 0 1)) ),
    my_3d_geometry_collection GEOMETRYCOLLECTIONM( POINTM(2 3 9), LINESTRINGM(2 3 4, 3 4 5) ),
    my_curve_polygon CURVEPOLYGON(CIRCULARSTRING(0 0, 4 0, 4 4, 0 4, 0 0),(1 1, 3 3, 3 1, 1 1)),
    my_multisurface MULTISURFACE(CURVEPOLYGON(CIRCULARSTRING(0 0, 4 0, 4 4, 0 4, 0 0),(1 1, 3 3, 3 1, 1 1)),((10 10, 14 12, 11 10,
10 10),(11 11, 11.5 11, 11 11.5, 11 11))),
    my_circularstring CIRCULARSTRING(0 0, 4 0, 4 4, 0 4, 0 0),
    PRIMARY KEY (quadkey)
);
