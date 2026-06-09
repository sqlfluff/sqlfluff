--------------------------------------
-- TPC-DS 93
--------------------------------------
SELECT ss_customer_sk,
               Sum(act_sales) sumsales
FROM   (SELECT ss_item_sk,
               ss_ticket_number,
               ss_customer_sk,
               CASE
                 WHEN sr_return_quantity IS NOT NULL THEN
                 ( ss_quantity - sr_return_quantity ) * ss_sales_price
                 ELSE ( ss_quantity * ss_sales_price )
               END act_sales
        FROM   store_sales
               LEFT OUTER JOIN store_returns
                            ON ( sr_item_sk = ss_item_sk
                                 AND sr_ticket_number = ss_ticket_number ),
               reason
        WHERE  sr_reason_sk = r_reason_sk
               AND r_reason_desc = 'reason 38') t
GROUP  BY ss_customer_sk
ORDER  BY sumsales,
          ss_customer_sk
LIMIT 100;
SELECT
  "store_sales"."ss_customer_sk" AS "ss_customer_sk",
  SUM(
    CASE
      WHEN NOT "store_returns"."sr_return_quantity" IS NULL
      THEN (
        "store_sales"."ss_quantity" - "store_returns"."sr_return_quantity"
      ) * "store_sales"."ss_sales_price"
      ELSE (
        "store_sales"."ss_quantity" * "store_sales"."ss_sales_price"
      )
    END
  ) AS "sumsales"
FROM "store_sales" AS "store_sales"
LEFT JOIN "store_returns" AS "store_returns"
  ON "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
  AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
JOIN "reason" AS "reason"
  ON "reason"."r_reason_desc" = 'reason 38'
WHERE
  "reason"."r_reason_sk" = "store_returns"."sr_reason_sk"
GROUP BY
  "store_sales"."ss_customer_sk"
ORDER BY
  "sumsales",
  "ss_customer_sk"
LIMIT 100;
