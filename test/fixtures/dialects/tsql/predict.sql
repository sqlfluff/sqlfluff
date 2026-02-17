-- Basic PREDICT with MODEL variable
SELECT d.*, p.*
FROM dbo.mytable AS d
CROSS APPLY PREDICT(
    MODEL = @model,
    DATA = d AS data
) WITH (prediction float) AS p;

-- PREDICT with model literal
SELECT d.*, p.*
FROM dbo.customers AS d
CROSS APPLY PREDICT(
    MODEL = my_model,
    DATA = d AS input_data
) WITH (
    predicted_value float,
    confidence float
) AS p;

-- PREDICT with RUNTIME parameter
SELECT d.*, p.*
FROM sales_data AS d
CROSS APPLY PREDICT(
    MODEL = @my_model,
    DATA = d AS t,
    RUNTIME = ONNX
) WITH (
    score float NOT NULL,
    category varchar(50)
) AS p;

-- PREDICT in FROM clause
SELECT *
FROM PREDICT(
    MODEL = @classification_model,
    DATA = dbo.test_data AS input
) WITH (
    class_label int,
    probability float
) AS predictions
WHERE predictions.probability > 0.8;

-- PREDICT with multiple result columns
SELECT customer_id, predicted_churn, churn_probability
FROM customers c
CROSS APPLY PREDICT(
    MODEL = churn_model,
    DATA = c AS customer_features
) WITH (
    predicted_churn bit NOT NULL,
    churn_probability decimal(5,4),
    segment varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS
) AS p;
