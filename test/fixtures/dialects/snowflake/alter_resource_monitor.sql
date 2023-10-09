alter resource monitor limiter
set
    credit_quota=2000
    notify_users = (jdoe, "jane smith", "john doe")
    FREQUENCY=DAILY
    start_timestamp = immediately
    end_timestamp = '2038-01-19 03:14:07'
    triggers
        on 80 percent do notify
        on 100 percent do suspend_immediate
;


ALTER RESOURCE MONITOR limiter
  SET CREDIT_QUOTA=2000
  TRIGGERS ON 80 PERCENT DO NOTIFY
           ON 100 PERCENT DO SUSPEND_IMMEDIATE
;
