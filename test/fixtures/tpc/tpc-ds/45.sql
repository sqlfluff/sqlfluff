--------------------------------------
-- TPC-DS 45
--------------------------------------
SELECT ca_zip,
               ca_state,
               Sum(ws_sales_price) AS "_col_2"
FROM   web_sales,
       customer,
       customer_address,
       date_dim,
       item
WHERE  ws_bill_customer_sk = c_customer_sk
       AND c_current_addr_sk = ca_address_sk
       AND ws_item_sk = i_item_sk
       AND ( SUBSTRING(ca_zip, 1, 5) IN ( '85669', '86197', '88274', '83405',
                                       '86475', '85392', '85460', '80348',
                                       '81792' )
              OR i_item_id IN (SELECT i_item_id
                               FROM   item
                               WHERE  i_item_sk IN ( 2, 3, 5, 7,
                                                     11, 13, 17, 19,
                                                     23, 29 )) )
       AND ws_sold_date_sk = d_date_sk
       AND d_qoy = 1
       AND d_year = 2000
GROUP  BY ca_zip,
          ca_state
ORDER  BY ca_zip,
          ca_state
LIMIT 100;
WITH "_u_0" AS (
  SELECT
    "item"."i_item_id" AS "i_item_id"
  FROM "item" AS "item"
  WHERE
    "item"."i_item_sk" IN (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
  GROUP BY
    "item"."i_item_id"
)
SELECT
  "customer_address"."ca_zip" AS "ca_zip",
  "customer_address"."ca_state" AS "ca_state",
  SUM("web_sales"."ws_sales_price") AS "_col_2"
FROM "web_sales" AS "web_sales"
JOIN "customer" AS "customer"
  ON "customer"."c_customer_sk" = "web_sales"."ws_bill_customer_sk"
JOIN "customer_address" AS "customer_address"
  ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  AND "date_dim"."d_qoy" = 1
  AND "date_dim"."d_year" = 2000
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."i_item_id" = "item"."i_item_id"
WHERE
  NOT "_u_0"."i_item_id" IS NULL
  OR SUBSTRING("customer_address"."ca_zip", 1, 5) IN ('85669', '86197', '88274', '83405', '86475', '85392', '85460', '80348', '81792')
GROUP BY
  "customer_address"."ca_zip",
  "customer_address"."ca_state"
ORDER BY
  "ca_zip",
  "ca_state"
LIMIT 100;
