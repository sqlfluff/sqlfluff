select
  u.user_id,
  u.user_email,
  p.product_id
from user_tb as u
inner join product_tb as p on u.user_id = p.user_id
  and position('@domain' in u.user_email) = 0;


SELECT position('#' IN tbl.col_a -> 'b') AS hash_pos FROM tbl;
