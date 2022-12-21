CREATE MODEL abalone_xgboost_multi_predict_age
FROM ( SELECT length_val,
              diameter,
              height,
              whole_weight,
              shucked_weight,
              viscera_weight,
              shell_weight,
              rings
        FROM abalone_xgb WHERE record_number < 2500 )
TARGET rings FUNCTION ml_fn_abalone_xgboost_multi_predict_age
IAM_ROLE 'arn:aws:iam::XXXXXXXXXXXX:role/Redshift-ML'
AUTO OFF
MODEL_TYPE XGBOOST
OBJECTIVE 'multi:softmax'
PREPROCESSORS 'none'
HYPERPARAMETERS DEFAULT EXCEPT (NUM_ROUND '100', NUM_CLASS '30')
SETTINGS (S3_BUCKET 'bucket');

CREATE MODEL customer_churn
FROM 'training-job-customer-churn-v4'
FUNCTION customer_churn_predict (varchar, int, float, float)
RETURNS int
IAM_ROLE 'arn:aws:iam::123456789012:role/Redshift-ML'
SETTINGS (S3_BUCKET 'bucket');

CREATE MODEL remote_customer_churn
FUNCTION remote_fn_customer_churn_predict (varchar, int, float, float)
RETURNS int
SAGEMAKER 'customer-churn-endpoint'
IAM_ROLE 'arn:aws:iam::0123456789012:role/Redshift-ML';

CREATE MODEL customers_clusters
FROM customers
FUNCTION customers_cluster
IAM_ROLE 'iam-role-arn'
AUTO OFF
MODEL_TYPE KMEANS
PREPROCESSORS '[
  {
    "ColumnSet": [ "*" ],
    "Transformers": [ "NumericPassthrough" ]
  }
]'
HYPERPARAMETERS DEFAULT EXCEPT ( K '5' )
SETTINGS (S3_BUCKET 'bucket');
