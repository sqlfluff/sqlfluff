begin
  -- variable based
  let somevariable := 5;
  let somevariable number(38, 0) := 5;
  let somevariable number(38, 0) default 5;
  let somevariable default 5;

  -- variable reassignment
  somevariable := 5;

  -- cursor based
  let somevariable cursor for select some_col from some_database.schema.some_table;
  let somevariable cursor for somevariable;
  let someresult resultset := (select some_col from some_database.schema.some_table);

  -- resultset reassignment
  someresult := (select SOME_COL from some_database.schema.some_table);
end;
