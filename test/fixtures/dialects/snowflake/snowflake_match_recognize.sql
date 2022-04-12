-- Examples from snowflake docs.
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

select price_date, match_number, msq, price, cl from
  (select * from stock_price_history where company='ABCD') match_recognize(
    order by price_date
    measures
        match_number() as "MATCH_NUMBER",
        match_sequence_number() as msq,
        classifier() as cl
    all rows per match
    pattern(any_row up+)
    define
        any_row as true,
        up as price > lag(price)
)
order by match_number, msq;

select * from stock_price_history match_recognize(
    partition by company
    order by price_date
    measures
        match_number() as "MATCH_NUMBER"
    all rows per match omit empty matches
    pattern(overavg*)
    define
        overavg as price > avg(price) over (rows between unbounded
                                  preceding and unbounded following)
)
order by company, price_date;

select * from stock_price_history match_recognize(
    partition by company
    order by price_date
    measures
        match_number() as "MATCH_NUMBER",
        classifier() as cl
    all rows per match with unmatched rows
    pattern(overavg+)
    define
        overavg as price > avg(price) over (rows between unbounded
                                 preceding and unbounded following)
)
order by company, price_date;

select company, price_date, price, "FINAL FIRST(LT45.price)", "FINAL LAST(LT45.price)"
    from stock_price_history
       match_recognize (
           partition by company
           order by price_date
           measures
               final first(lt45.price) as "FINAL FIRST(LT45.price)",
               final last(lt45.price)  as "FINAL LAST(LT45.price)"
           all rows per match
           after match skip past last row
           pattern (lt45 lt45)
           define
               lt45 as price < 45.00
           )
    where company = 'ABCD'
    order by price_date;

-- Testing all quantifiers.
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
    pattern(^ S1+ S2* S3? S4{1} S5{1,} S6{,1} S7{1,1} S8*? $)
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;

-- Testing operators.
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
    pattern(^ ( S1 | S2* )? S3 PERMUTE(S4+, S5*?) {- S6 -}+ $)
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;

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
    pattern((A {- B+ C+ -} D+))
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;

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
    pattern((A | B){5} C+)
    define
      row_with_price_decrease as price < lag(price),
      row_with_price_increase as price > lag(price)
  )
order by company, match_number;
