EXECUTE IMMEDIATE 'select 1';

EXECUTE IMMEDIATE $$
  SELECT PI();
$$;

SET pie =
$$
  SELECT PI();
$$
;

SET one = 1;
SET two = 2;

EXECUTE IMMEDIATE $pie;
EXECUTE IMMEDIATE $pie USING (one, two);

SET three = 'select ? + ?';
EXECUTE IMMEDIATE :three;
EXECUTE IMMEDIATE :three USING (one, two);
