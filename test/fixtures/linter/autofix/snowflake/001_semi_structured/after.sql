select
    value:data:to::string AS to_phone_number,
    value:data:from::string AS from_phone_number
FROM a.b.ticket_audits
