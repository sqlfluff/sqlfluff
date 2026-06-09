--------------------------------------
-- TPC-H 22
--------------------------------------
select
        cntrycode,
        count(*) as numcust,
        sum(c_acctbal) as totacctbal
from
        (
                select
                        substring(c_phone, 1, 2) as cntrycode,
                        c_acctbal
                from
                        customer
                where
                        substring(c_phone, 1, 2) in
                                ('13', '31', '23', '29', '30', '18', '17')
                        and c_acctbal > (
                                select
                                        avg(c_acctbal)
                                from
                                        customer
                                where
                                        c_acctbal > 0.00
                                        and substring(c_phone, 1, 2) in
                                                ('13', '31', '23', '29', '30', '18', '17')
                        )
                        and not exists (
                                select
                                        *
                                from
                                        orders
                                where
                                        o_custkey = c_custkey
                        )
        ) as custsale
group by
        cntrycode
order by
        cntrycode;
WITH "_u_0" AS (
  SELECT
    AVG("customer"."c_acctbal") AS "_col_0"
  FROM "customer" AS "customer"
  WHERE
    "customer"."c_acctbal" > 0.00
    AND SUBSTRING("customer"."c_phone", 1, 2) IN ('13', '31', '23', '29', '30', '18', '17')
), "_u_1" AS (
  SELECT
    "orders"."o_custkey" AS "_u_2"
  FROM "orders" AS "orders"
  GROUP BY
    "orders"."o_custkey"
)
SELECT
  SUBSTRING("customer"."c_phone", 1, 2) AS "cntrycode",
  COUNT(*) AS "numcust",
  SUM("customer"."c_acctbal") AS "totacctbal"
FROM "customer" AS "customer"
JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_col_0" < "customer"."c_acctbal"
LEFT JOIN "_u_1" AS "_u_1"
  ON "_u_1"."_u_2" = "customer"."c_custkey"
WHERE
  "_u_1"."_u_2" IS NULL
  AND SUBSTRING("customer"."c_phone", 1, 2) IN ('13', '31', '23', '29', '30', '18', '17')
GROUP BY
  SUBSTRING("customer"."c_phone", 1, 2)
ORDER BY
  "cntrycode";
