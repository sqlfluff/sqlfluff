CREATE TABLE public.foo
(
    my_point POINT(0 0),
    my_simple_polygon POLYGON((0 0 , 1 0, 1 1, 0 1, 0 0)),
    my_geometry_column GEOMETRY (GEOMETRY, 4326)
);
