SELECT
    *
FROM
    ML.PREDICT(
        MODEL `project.dataset.model`,
        (
            SELECT
                user_id
            FROM
                `project.dataset.stats`
        )
    )
