CREATE TEMP FUNCTION parseTopSellers(arr_str STRING)
RETURNS ARRAY<STRUCT<product_id INT64, rating FLOAT64>>
LANGUAGE js
OPTIONS
(
    library=["gs://my-bucket/path/to/lib1.js", "gs://my-bucket/path/to/lib2.js"]
)
AS """
    CODE GOES HERE
"""
