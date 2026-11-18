CREATE AGGREGATE agg_twocols(numeric, numeric) (
   SFUNC = mysfunc_accum,
   STYPE = numeric,
   COMBINEFUNC = mycombine_accum,
   INITCOND = 0
);

CREATE AGGREGATE agg_array_stype(numeric[]) (
   SFUNC = mysfunc_accum,
   STYPE = numeric[]
);
