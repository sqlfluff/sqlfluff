COPY INTO '@public.dir/airflow-pipelines/'
            FROM "MODEL"."FCT_ROLLING_ACTIVE_USERS_L28"
            FILE_FORMAT = (TYPE = PARQUET)
            SINGLE = FALSE
            MAX_FILE_SIZE = 1000000000
            INCLUDE_QUERY_ID = TRUE
			HEADER = TRUE;

-- mixed order between `copyOptions` and other copy configurations
COPY INTO 's3://geotags.csv.gz'
FROM
(
  SELECT DISTINCT
    ID,
    CAST(Z.VALUE AS INTEGER) AS LISTING_ADDRESS_POSTALCODE
  FROM
    ANALYTICS_PROD.SERVICE.GEO_DATA_LAYER_FLATTEN,
    LATERAL FLATTEN(ZIPS) AS Z
  WHERE
    TYPE IN ('canton', 'region', 'zip')
    AND PARENTPATHS LIKE '%geo-country-switzerland%'
) STORAGE_INTEGRATION = SI_S3_DS_ASSETS FILE_FORMAT = (
  TYPE = CSV NULL_IF = () EMPTY_FIELD_AS_NULL = FALSE COMPRESSION = GZIP
) SINGLE = TRUE OVERWRITE = TRUE HEADER = TRUE MAX_FILE_SIZE = 5368709120;

-- with a CTE in the query segment
COPY INTO @my_stage/path/to/file.json.gz
FROM
(
  WITH my_cte AS (
    SELECT 1
  )
  SELECT *
  FROM my_cte
);
