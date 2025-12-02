create resource monitor if not exists test;


create or replace resource monitor limiter with credit_quota = 1;
create or replace resource monitor test with frequency = monthly;

create or replace resource monitor limiter with start_timestamp = immediately;
create or replace resource monitor limiter with start_timestamp= '2038-01-19 03:14:07';

create or replace resource monitor limiter with
credit_quota = 100
NOTIFY_USERS = (joe, "sara", "ashlee")
start_timestamp = immediately
end_timestamp = '2038-01-19 03:14:07'
;

create or replace resource monitor limiter with credit_quota=5000
  notify_users = (jdoe, "jane smith", "john doe")
  triggers on 75 percent do notify
           on 100 percent do suspend
           on 110 percent do suspend_immediate
;
