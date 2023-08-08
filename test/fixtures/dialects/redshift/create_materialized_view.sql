create materialized view mat_view_example
backup yes
auto refresh no
as
select col1
from example_table;


CREATE MATERIALIZED VIEW tickets_mv AS
    select   catgroup,
    sum(qtysold) as sold
    from     category c, event e, sales s
    where    c.catid = e.catid
    and      e.eventid = s.eventid
    group by catgroup;


CREATE MATERIALIZED VIEW mv_sales_vw as
select salesid, qtysold, pricepaid, commission, saletime from public.sales
union all
select salesid, qtysold, pricepaid, commission, saletime from spectrum.sales
;


CREATE MATERIALIZED VIEW mv_baseball 
DISTSTYLE ALL 
AUTO REFRESH YES 
AS 
SELECT ball  AS baseball 
FROM baseball_table;
