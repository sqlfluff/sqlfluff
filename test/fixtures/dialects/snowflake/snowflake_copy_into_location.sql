COPY INTO '@public.dir/airflow-pipelines/'
            FROM "MODEL"."FCT_ROLLING_ACTIVE_USERS_L28"
            FILE_FORMAT = (TYPE = PARQUET)
            SINGLE = FALSE
            MAX_FILE_SIZE = 1000000000
            INCLUDE_QUERY_ID = TRUE
			HEADER = TRUE

			
			
Sequence(
            OneOf(
                "RECORD_DELIMITER",
                "FIELD_DELIMITER",
                "ESCAPE",
                "ESCAPE_UNENCLOSED_FIELD",
                "FIELD_OPTIONALLY_ENCLOSED_BY",
            ),
            Ref("EqualsSegment"),
            OneOf("NONE", Ref("QuotedLiteralSegment")),
        ),