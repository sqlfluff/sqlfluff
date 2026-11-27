CREATE MODEL sentiment_model
INPUT (text STRING)
OUTPUT (label STRING, score DOUBLE)
COMMENT 'sentiment classification model'
WITH (
    'provider' = 'openai',
    'endpoint' = 'https://api.openai.com/v1/chat/completions'
);

CREATE TEMPORARY MODEL IF NOT EXISTS my_db.local_model
WITH (
    'provider' = 'local'
);

CREATE MODEL trained_model
INPUT (x DOUBLE)
OUTPUT (y DOUBLE)
WITH (
    'provider' = 'local'
)
AS
SELECT
    x,
    y
FROM training_data;

ALTER MODEL IF EXISTS sentiment_model SET ('model-version' = 'v2');

ALTER MODEL sentiment_model RESET ('model-version');

ALTER MODEL sentiment_model RENAME TO sentiment_model_v2;

DROP MODEL IF EXISTS sentiment_model_v2;

DROP TEMPORARY MODEL IF EXISTS my_db.local_model;
