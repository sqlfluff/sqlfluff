insert overwrite into forecast_daily_product_base
with orders_monthly as (
      select
          period, status, region, forecast_id, value
      from forecast_monthly
      where metric = 'orders'
  ),
  penetrations_monthly as (
        select
            period, status, region,
            product_category, forecast_id, value
        from forecast_monthly
        where metric = 'penetration'

        union all

        -- Add in the dry penetrations as 1.0
        select
            period, status, region,
            'dry' as product_category,
            forecast_id, 1.0 as value
        from forecast_monthly
        where metric = 'orders'
    )
select * from orders_monthly
inner join penetrations_monthly
using(period, status, region, forecast_id)
