select
    {{some_field}},
    (1+2 ) AS kev,
  "wrongly indented field" as something_else,
    trailing_whitespace    ,    
    4678.9
  from {{my_table}}
 where indentation  = "wrong" AND    NotSpacedProperly
 AND 4+6 > 9
    