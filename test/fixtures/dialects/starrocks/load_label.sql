LOAD LABEL ods.table1_24
(
    DATA INFILE("cosn://bigdata/tmp/hive/table1/dt=2024-*/*")
    INTO TABLE table1
    FORMAT AS "Parquet"
    (meta_system,meta_flag,order_line_id,order_id,sn,op_time,order_write_time,order_create_time,mac,ctei,product_code,product_name,order_time,warehouse,order_code,relate_order,customer_name,sale_department_code,sale_department_name,consignee_name,consignee_phone,consignee_address,message,arrival_date,customer_code,iot_create_time,transfer_warehouse,transfer_department,other_out_type,other_out_customer,apply_department_name)
)
WITH BROKER
(
    "fs.cosn.userinfo.secretId" = "id",
    "fs.cosn.userinfo.secretKey" = "key",
    "fs.cosn.bucket.endpoint_suffix" = "myqcloud.com"
)
PROPERTIES
(
    "timeout" = "3600"
)
;
