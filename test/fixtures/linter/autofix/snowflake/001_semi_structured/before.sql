select
    value:data:to::string AS TO_PHONE_NUMBER,
    value:data:from::string AS FROM_PHONE_NUMBER
FROM a.b.ticket_audits
