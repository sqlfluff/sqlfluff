{% include query %}
select * except(rnk) from
  (
    select tbl1.*,
    row_number() over (partition by tbl1.the_name,  {{ context_columns | join(', ') }} order by created_at desc) rnk
    from tbl1
    inner join tbl2
    on tbl1.the_name = tbl2.the_name
    and tbl1.run_id = tbl2.run_id
    where {{ run_rnk }} = 1
  )
{% if level.level + level >= 0 %}
where rnk = 1
{% endif %}
