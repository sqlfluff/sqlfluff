--------------------------------------
-- TPC-DS 41
--------------------------------------
SELECT Distinct(i_product_name)
FROM   item i1
WHERE  i_manufact_id BETWEEN 765 AND 765 + 40
       AND (SELECT Count(*) AS item_cnt
            FROM   item
            WHERE  ( i_manufact = i1.i_manufact
                     AND ( ( i_category = 'Women'
                             AND ( i_color = 'dim'
                                    OR i_color = 'green' )
                             AND ( i_units = 'Gross'
                                    OR i_units = 'Dozen' )
                             AND ( i_size = 'economy'
                                    OR i_size = 'petite' ) )
                            OR ( i_category = 'Women'
                                 AND ( i_color = 'navajo'
                                        OR i_color = 'aquamarine' )
                                 AND ( i_units = 'Case'
                                        OR i_units = 'Unknown' )
                                 AND ( i_size = 'large'
                                        OR i_size = 'N/A' ) )
                            OR ( i_category = 'Men'
                                 AND ( i_color = 'indian'
                                        OR i_color = 'dark' )
                                 AND ( i_units = 'Oz'
                                        OR i_units = 'Lb' )
                                 AND ( i_size = 'extra large'
                                        OR i_size = 'small' ) )
                            OR ( i_category = 'Men'
                                 AND ( i_color = 'peach'
                                        OR i_color = 'purple' )
                                 AND ( i_units = 'Tbl'
                                        OR i_units = 'Bunch' )
                                 AND ( i_size = 'economy'
                                        OR i_size = 'petite' ) ) ) )
                    OR ( i_manufact = i1.i_manufact
                         AND ( ( i_category = 'Women'
                                 AND ( i_color = 'orchid'
                                        OR i_color = 'peru' )
                                 AND ( i_units = 'Carton'
                                        OR i_units = 'Cup' )
                                 AND ( i_size = 'economy'
                                        OR i_size = 'petite' ) )
                                OR ( i_category = 'Women'
                                     AND ( i_color = 'violet'
                                            OR i_color = 'papaya' )
                                     AND ( i_units = 'Ounce'
                                            OR i_units = 'Box' )
                                     AND ( i_size = 'large'
                                            OR i_size = 'N/A' ) )
                                OR ( i_category = 'Men'
                                     AND ( i_color = 'drab'
                                            OR i_color = 'grey' )
                                     AND ( i_units = 'Each'
                                            OR i_units = 'N/A' )
                                     AND ( i_size = 'extra large'
                                            OR i_size = 'small' ) )
                                OR ( i_category = 'Men'
                                     AND ( i_color = 'chocolate'
                                            OR i_color = 'antique' )
                                     AND ( i_units = 'Dram'
                                            OR i_units = 'Gram' )
                                     AND ( i_size = 'economy'
                                            OR i_size = 'petite' ) ) ) )) > 0
ORDER  BY i_product_name
LIMIT 100;
SELECT DISTINCT
  "i1"."i_product_name" AS "i_product_name"
FROM "item" AS "i1"
WHERE
  "i1"."i_manufact_id" <= 805
  AND "i1"."i_manufact_id" >= 765
  AND (
    SELECT
      COUNT(*) AS "item_cnt"
    FROM "item" AS "item"
    WHERE
      (
        "i1"."i_manufact" = "item"."i_manufact"
        AND (
          (
            "item"."i_category" = 'Men'
            AND (
              "item"."i_color" = 'antique' OR "item"."i_color" = 'chocolate'
            )
            AND (
              "item"."i_size" = 'economy' OR "item"."i_size" = 'petite'
            )
            AND (
              "item"."i_units" = 'Dram' OR "item"."i_units" = 'Gram'
            )
          )
          OR (
            "item"."i_category" = 'Men'
            AND (
              "item"."i_color" = 'drab' OR "item"."i_color" = 'grey'
            )
            AND (
              "item"."i_size" = 'extra large' OR "item"."i_size" = 'small'
            )
            AND (
              "item"."i_units" = 'Each' OR "item"."i_units" = 'N/A'
            )
          )
          OR (
            "item"."i_category" = 'Women'
            AND (
              "item"."i_color" = 'orchid' OR "item"."i_color" = 'peru'
            )
            AND (
              "item"."i_size" = 'economy' OR "item"."i_size" = 'petite'
            )
            AND (
              "item"."i_units" = 'Carton' OR "item"."i_units" = 'Cup'
            )
          )
          OR (
            "item"."i_category" = 'Women'
            AND (
              "item"."i_color" = 'papaya' OR "item"."i_color" = 'violet'
            )
            AND (
              "item"."i_size" = 'N/A' OR "item"."i_size" = 'large'
            )
            AND (
              "item"."i_units" = 'Box' OR "item"."i_units" = 'Ounce'
            )
          )
        )
      )
      OR (
        "i1"."i_manufact" = "item"."i_manufact"
        AND (
          (
            "item"."i_category" = 'Men'
            AND (
              "item"."i_color" = 'dark' OR "item"."i_color" = 'indian'
            )
            AND (
              "item"."i_size" = 'extra large' OR "item"."i_size" = 'small'
            )
            AND (
              "item"."i_units" = 'Lb' OR "item"."i_units" = 'Oz'
            )
          )
          OR (
            "item"."i_category" = 'Men'
            AND (
              "item"."i_color" = 'peach' OR "item"."i_color" = 'purple'
            )
            AND (
              "item"."i_size" = 'economy' OR "item"."i_size" = 'petite'
            )
            AND (
              "item"."i_units" = 'Bunch' OR "item"."i_units" = 'Tbl'
            )
          )
          OR (
            "item"."i_category" = 'Women'
            AND (
              "item"."i_color" = 'aquamarine' OR "item"."i_color" = 'navajo'
            )
            AND (
              "item"."i_size" = 'N/A' OR "item"."i_size" = 'large'
            )
            AND (
              "item"."i_units" = 'Case' OR "item"."i_units" = 'Unknown'
            )
          )
          OR (
            "item"."i_category" = 'Women'
            AND (
              "item"."i_color" = 'dim' OR "item"."i_color" = 'green'
            )
            AND (
              "item"."i_size" = 'economy' OR "item"."i_size" = 'petite'
            )
            AND (
              "item"."i_units" = 'Dozen' OR "item"."i_units" = 'Gross'
            )
          )
        )
      )
  ) > 0
ORDER BY
  "i1"."i_product_name"
LIMIT 100;
