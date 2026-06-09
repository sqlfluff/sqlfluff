--------------------------------------
-- TPC-DS 85
--------------------------------------
SELECT SUBSTRING(r_reason_desc, 1, 20) AS "_col_0",
               Avg(ws_quantity) AS "_col_1",
               Avg(wr_refunded_cash) AS "_col_2",
               Avg(wr_fee) AS "_col_3"
FROM   web_sales,
       web_returns,
       web_page,
       customer_demographics cd1,
       customer_demographics cd2,
       customer_address,
       date_dim,
       reason
WHERE  ws_web_page_sk = wp_web_page_sk
       AND ws_item_sk = wr_item_sk
       AND ws_order_number = wr_order_number
       AND ws_sold_date_sk = d_date_sk
       AND d_year = 2001
       AND cd1.cd_demo_sk = wr_refunded_cdemo_sk
       AND cd2.cd_demo_sk = wr_returning_cdemo_sk
       AND ca_address_sk = wr_refunded_addr_sk
       AND r_reason_sk = wr_reason_sk
       AND ( ( cd1.cd_marital_status = 'W'
               AND cd1.cd_marital_status = cd2.cd_marital_status
               AND cd1.cd_education_status = 'Primary'
               AND cd1.cd_education_status = cd2.cd_education_status
               AND ws_sales_price BETWEEN 100.00 AND 150.00 )
              OR ( cd1.cd_marital_status = 'D'
                   AND cd1.cd_marital_status = cd2.cd_marital_status
                   AND cd1.cd_education_status = 'Secondary'
                   AND cd1.cd_education_status = cd2.cd_education_status
                   AND ws_sales_price BETWEEN 50.00 AND 100.00 )
              OR ( cd1.cd_marital_status = 'M'
                   AND cd1.cd_marital_status = cd2.cd_marital_status
                   AND cd1.cd_education_status = 'Advanced Degree'
                   AND cd1.cd_education_status = cd2.cd_education_status
                   AND ws_sales_price BETWEEN 150.00 AND 200.00 ) )
       AND ( ( ca_country = 'United States'
               AND ca_state IN ( 'KY', 'ME', 'IL' )
               AND ws_net_profit BETWEEN 100 AND 200 )
              OR ( ca_country = 'United States'
                   AND ca_state IN ( 'OK', 'NE', 'MN' )
                   AND ws_net_profit BETWEEN 150 AND 300 )
              OR ( ca_country = 'United States'
                   AND ca_state IN ( 'FL', 'WI', 'KS' )
                   AND ws_net_profit BETWEEN 50 AND 250 ) )
GROUP  BY r_reason_desc
ORDER  BY SUBSTRING(r_reason_desc, 1, 20),
          Avg(ws_quantity),
          Avg(wr_refunded_cash),
          Avg(wr_fee)
LIMIT 100;
SELECT
  SUBSTRING("reason"."r_reason_desc", 1, 20) AS "_col_0",
  AVG("web_sales"."ws_quantity") AS "_col_1",
  AVG("web_returns"."wr_refunded_cash") AS "_col_2",
  AVG("web_returns"."wr_fee") AS "_col_3"
FROM "web_sales" AS "web_sales"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  AND "date_dim"."d_year" = 2001
JOIN "web_page" AS "web_page"
  ON "web_page"."wp_web_page_sk" = "web_sales"."ws_web_page_sk"
JOIN "web_returns" AS "web_returns"
  ON "web_returns"."wr_item_sk" = "web_sales"."ws_item_sk"
  AND "web_returns"."wr_order_number" = "web_sales"."ws_order_number"
JOIN "customer_demographics" AS "cd1"
  ON "cd1"."cd_demo_sk" = "web_returns"."wr_refunded_cdemo_sk"
JOIN "customer_address" AS "customer_address"
  ON "customer_address"."ca_address_sk" = "web_returns"."wr_refunded_addr_sk"
  AND (
    (
      "customer_address"."ca_country" = 'United States'
      AND "customer_address"."ca_state" IN ('FL', 'WI', 'KS')
      AND "web_sales"."ws_net_profit" <= 250
      AND "web_sales"."ws_net_profit" >= 50
    )
    OR (
      "customer_address"."ca_country" = 'United States'
      AND "customer_address"."ca_state" IN ('KY', 'ME', 'IL')
      AND "web_sales"."ws_net_profit" <= 200
      AND "web_sales"."ws_net_profit" >= 100
    )
    OR (
      "customer_address"."ca_country" = 'United States'
      AND "customer_address"."ca_state" IN ('OK', 'NE', 'MN')
      AND "web_sales"."ws_net_profit" <= 300
      AND "web_sales"."ws_net_profit" >= 150
    )
  )
JOIN "reason" AS "reason"
  ON "reason"."r_reason_sk" = "web_returns"."wr_reason_sk"
JOIN "customer_demographics" AS "cd2"
  ON "cd2"."cd_demo_sk" = "web_returns"."wr_returning_cdemo_sk"
  AND (
    (
      "cd1"."cd_education_status" = "cd2"."cd_education_status"
      AND "cd1"."cd_education_status" = 'Advanced Degree'
      AND "cd1"."cd_marital_status" = "cd2"."cd_marital_status"
      AND "cd1"."cd_marital_status" = 'M'
      AND "web_sales"."ws_sales_price" <= 200.00
      AND "web_sales"."ws_sales_price" >= 150.00
    )
    OR (
      "cd1"."cd_education_status" = "cd2"."cd_education_status"
      AND "cd1"."cd_education_status" = 'Primary'
      AND "cd1"."cd_marital_status" = "cd2"."cd_marital_status"
      AND "cd1"."cd_marital_status" = 'W'
      AND "web_sales"."ws_sales_price" <= 150.00
      AND "web_sales"."ws_sales_price" >= 100.00
    )
    OR (
      "cd1"."cd_education_status" = "cd2"."cd_education_status"
      AND "cd1"."cd_education_status" = 'Secondary'
      AND "cd1"."cd_marital_status" = "cd2"."cd_marital_status"
      AND "cd1"."cd_marital_status" = 'D'
      AND "web_sales"."ws_sales_price" <= 100.00
      AND "web_sales"."ws_sales_price" >= 50.00
    )
  )
GROUP BY
  "reason"."r_reason_desc"
ORDER BY
  "_col_0",
  "_col_1",
  "_col_2",
  "_col_3"
LIMIT 100;
