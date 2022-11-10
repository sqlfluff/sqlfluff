COPY INTO '@public.cb_data_archive_prod/airflow-pipelines/2022-11-01/model/fct_rolling_active_users_l28/'
            FROM "MODEL"."FCT_ROLLING_ACTIVE_USERS_L28"
            FILE_FORMAT = (TYPE = PARQUET)
            SINGLE = FALSE
            MAX_FILE_SIZE = 1000000000
            INCLUDE_QUERY_ID = TRUE
			HEADER = TRUE