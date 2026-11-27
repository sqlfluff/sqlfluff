SELECT *
FROM my_ptf(
    input => TABLE events PARTITION BY user_id ORDER BY event_time,
    on_time => DESCRIPTOR(event_time)
);

SELECT *
FROM my_ptf(
    input => TABLE (
        SELECT
            user_id,
            region,
            event_time
        FROM events
    ) PARTITION BY (user_id, region) ORDER BY (event_time ASC NULLS LAST, user_id DESC),
    cols => DESCRIPTOR(user_id, region)
);

SELECT *
FROM ML_PREDICT(
    INPUT => TABLE input_texts,
    MODEL => MODEL sentiment_model,
    ARGS => DESCRIPTOR(text)
);

SELECT *
FROM ML_PREDICT(
    TABLE input_texts,
    MODEL sentiment_model,
    DESCRIPTOR(text)
);

SELECT *
FROM VECTOR_SEARCH(
    TABLE documents,
    DESCRIPTOR(embedding),
    ARRAY[0.1, 0.2, 0.3],
    10
);

SELECT *
FROM FROM_CHANGELOG(
    input => TABLE raw_cdc,
    op_mapping => MAP['I', '+I', 'D', '-D']
);

SELECT *
FROM TO_CHANGELOG(
    input => TABLE dynamic_orders
);
