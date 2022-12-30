with source as (

    select *
    from {{ "schema1" + "." + "table1" }}

)

select * from source

{% if False %}

    -- this filter will only be applied on an incremental run
    where sysstarttime > (select max(sysstarttime) from schema1.table2)

{% endif %}
