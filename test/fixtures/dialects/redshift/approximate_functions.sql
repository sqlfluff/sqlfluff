select top 10 date.caldate,
count(totalprice), sum(totalprice),
approximate percentile_disc(0.5)
within group (order by totalprice)
from listing
join date on listing.dateid = date.dateid
group by date.caldate;

select approximate count(distinct pricepaid) from sales;

select count(distinct pricepaid) from sales;

select approximate(foo) from bar;
