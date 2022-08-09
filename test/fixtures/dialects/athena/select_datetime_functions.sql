-- https://prestodb.io/docs/0.217/functions/datetime.html

select date '2012-08-08' + interval '2' day;

select time '01:00' + interval '3' hour;

select timestamp '2012-08-08 01:00' + interval '29' hour;

select timestamp '2012-10-31 01:00' + interval '1' month;

select interval '2' day + interval '3' hour;

select interval '3' year + interval '5' month;

select date '2012-08-08' - interval '2' day;

select time '01:00' - interval '3' hour;

select timestamp '2012-08-08 01:00' - interval '29' hour;

select timestamp '2012-10-31 01:00' - interval '1' month;

select interval '2' day - interval '3' hour;

select interval '3' year - interval '5' month;

select current_time;

select current_date;

select current_timestamp;

select current_timezone();

select date('1970-01-01');

select cast('1970-01-01' as date);

select from_iso8601_timestamp('2019-09-07T-15:50+00');

select from_iso8601_date('2019-09-07T-15:50+00');

select from_unixtime(1556285138);

select localtime;

select localtimestamp;

select now();

select to_iso8601('1970-01-01');

select to_unixtime(current_timestamp);
