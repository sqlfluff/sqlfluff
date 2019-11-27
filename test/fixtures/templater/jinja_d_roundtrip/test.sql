select
    {{some_field}},
    (1+2 )  AS kev,
  "wrongly indented field" as something_else,
    trailing_whitespace    ,    
    4678.9
FROM  {{my_table}}
 WHERE indentation  = "wrong" and    NotSpacedProperly
    