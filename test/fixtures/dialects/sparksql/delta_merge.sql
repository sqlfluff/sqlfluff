-- upsert into a table
MERGE INTO people10m
USING people10mupdates
    ON people10m.id = people10mupdates.id
WHEN MATCHED THEN
    UPDATE SET
        id = people10mupdates.id,
        first_name = people10mupdates.first_name,
        middle_name = people10mupdates.middle_name,
        last_name = people10mupdates.last_name,
        gender = people10mupdates.gender,
        birth_date = people10mupdates.birth_date,
        ssn = people10mupdates.ssn,
        salary = people10mupdates.salary
WHEN NOT MATCHED THEN
    INSERT (
        id,
        first_name,
        middle_name,
        last_name,
        gender,
        birth_date,
        ssn,
        salary
    )
    VALUES (
        people10mupdates.id,
        people10mupdates.first_name,
        people10mupdates.middle_name,
        people10mupdates.last_name,
        people10mupdates.gender,
        people10mupdates.birth_date,
        people10mupdates.ssn,
        people10mupdates.salary
    );

-- data deduplication
MERGE INTO logs
USING new_deduped_logs
    ON logs.unique_id = new_deduped_logs.unique_id
WHEN NOT MATCHED THEN
    INSERT *;

-- data deduplication with additional predicate
MERGE INTO
    logs
USING
    new_deduped_logs
    ON logs.unique_id = new_deduped_logs.unique_id
       AND logs.date > current_date() - INTERVAL 7 DAYS
WHEN NOT MATCHED
AND new_deduped_logs.date > current_date() - INTERVAL 7 DAYS THEN
    INSERT *;

-- SCD Type 2 using MERGE
MERGE INTO
    customers
USING (
    SELECT
        updates.customer_id AS merge_unique_key,
        updates.*
    FROM updates
    UNION ALL
    SELECT
        NULL AS merge_unique_key,
        updates.*
    FROM updates INNER JOIN customers
        ON updates.customer_id = customers.customer_id
    WHERE customers.current = TRUE AND updates.address != customers.address
) staged_updates
ON customers.customer_id = merge_unique_key
WHEN MATCHED
AND customers.current = TRUE
AND customers.address != staged_updates.address THEN
    UPDATE SET current = FALSE, end_date = staged_updates.effective_date
WHEN NOT MATCHED THEN
    INSERT(
        customer_id,
        address,
        current,
        effective_date,
        end_date
    )
    VALUES(
        staged_updates.customer_id,
        staged_updates.address,
        TRUE,
        staged_updates.effective_date,
        NULL
    );

-- ingest CDC using MERGE
MERGE INTO target t
USING (
    SELECT
        changes.unique_key,
        changes.latest.new_value AS new_value,
        changes.latest.deleted AS deleted
    FROM (
        SELECT
            unique_key,
            max(struct(change_time, new_value, deleted)) AS latest
        FROM changes
        GROUP BY unique_key
    )
) s
ON s.unique_key = t.unique_key
WHEN MATCHED AND s.deleted = TRUE THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET unique_key = s.unique_key, record_value = s.new_value
WHEN NOT MATCHED AND s.deleted = FALSE THEN
    INSERT (
        unique_key,
        record_value
    )
    VALUES (
        unique_key,
        new_value
    );
