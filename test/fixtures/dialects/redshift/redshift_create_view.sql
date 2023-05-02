create view sales_vw as
select * from public.sales
union all
select * from spectrum.sales
with no schema binding;
