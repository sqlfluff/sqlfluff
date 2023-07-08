COPY INTO '@public.dir/airflow-pipelines/'
            FROM "MODEL"."FCT_ROLLING_ACTIVE_USERS_L28"
            FILE_FORMAT = (TYPE = PARQUET)
            SINGLE = FALSE
            MAX_FILE_SIZE = 1000000000
            INCLUDE_QUERY_ID = TRUE
			HEADER = TRUE
