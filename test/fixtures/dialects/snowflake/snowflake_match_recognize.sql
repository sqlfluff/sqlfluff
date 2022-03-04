select * from stock_price_history
  match_recognize(
    partition by company
    order by price_date
    measures
      match_number() as match_number,
      first(price_date) as start_date,
      last(price_date) as end_date,
      count(*) as rows_in_sequence,
      count(row_with_price_decrease.*) as num_decreases,
      count(row_with_price_increase.*) as num_increases
    one row per match
    after match skip to last row_with_price_increase
    pattern(row_before_decrease row_with_price_decrease+ row_with_price_increase+)
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;

-- With more complicated pattern
select * from stock_price_history
  match_recognize(
    partition by company
    order by price_date
    measures
      match_number() as match_number,
      first(price_date) as start_date,
      last(price_date) as end_date,
      count(*) as rows_in_sequence,
      count(row_with_price_decrease.*) as num_decreases,
      count(row_with_price_increase.*) as num_increases
    one row per match
    after match skip to last row_with_price_increase
    pattern(^ S1+ S2* S3? S4{1} S5{1,} S6{,1} S7{1,1} $)
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;
