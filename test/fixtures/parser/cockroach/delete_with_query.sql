delete from t2 pd
where exists (
  select 1 from t2
  where b = pd.b and c = pd.c and d != pd.d
);
