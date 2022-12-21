with last_day_macro as (

select
    
  cast(
        
  

    
  

    
    date_trunc('month', 2021-11-05)
 + ((interval '1 month') * (1))


 + ((interval '1 day') * (-1))



        as date)


)

select * from last_day_macro
