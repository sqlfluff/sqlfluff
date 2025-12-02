declare curs1 cursor for
select col1, col2 from tbl1;

declare lollapalooza cursor for
select eventname, starttime, pricepaid/qtysold as costperticket, qtysold
from sales, event
where sales.eventid = event.eventid
and eventname = 'lollapalooza';
