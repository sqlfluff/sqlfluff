SELECT
        *
    FROM
        superverylongtablenamereallyreally1
    WHERE
        long_varname_to_trigger_Rule_LT05_id in (SELECT distinct id FROM superverylongtablenamereallyreally2 WHERE deletedat IS NULL)
