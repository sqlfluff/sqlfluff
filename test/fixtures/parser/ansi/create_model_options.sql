CREATE OR REPLACE MODEL model3
OPTIONS (
    MODEL_TYPE='LOGISTIC_REG',
    AUTO_CLASS_WEIGHTS=TRUE,
    INPUT_LABEL_COLS = ['label_str']
)
AS
SELECT
    a,
    b
FROM
    table1
WHERE
    training = 1
