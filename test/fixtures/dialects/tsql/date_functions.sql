select convert(
        date,
        dateadd(
            month,
            datediff(
                month,
                0,
                t.valid_from_date
            ),
            0
        )
    ) as valid_from_date
from t as t
where t.activity_month >=
    convert(
        date,
        dateadd(
            yy,
            datediff(yy, 0, getdate()
        ) - 1, 0)
    )
