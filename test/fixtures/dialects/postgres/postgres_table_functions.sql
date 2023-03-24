select * from unnest(array['123', '456']);

select * from unnest(array['123', '456']) as a(val, row_num);

select * from unnest(array['123', '456']) with ordinality;

select * from unnest(array['123', '456']) with ordinality as a(val, row_num);
