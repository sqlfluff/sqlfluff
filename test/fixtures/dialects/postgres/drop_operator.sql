DROP OPERATOR ^^ (text, text);

DROP OPERATOR IF EXISTS bob.!== (box, box);

DROP OPERATOR IF EXISTS ~~~ (character varying, text[]), !! (NONE, integer) CASCADE;

DROP OPERATOR public.<<-> (double precision, double precision) RESTRICT;

DROP OPERATOR IF EXISTS === (box, box);
