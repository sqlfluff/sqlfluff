select * except({% include query %}) from
  (
    select tbl1.*,
    row_number() over (partition by tbl1.the_name,  {{ context_columns | join(', ') }} order by created_at desc) rnk
    {% if context_columns | default("abc") == "abc" %}
    from tbl1
    {% endif %}
    inner join tbl2
    on tbl1.the_name = tbl2.the_name
    and tbl1.run_id = tbl2.run_id
    where {{ run_rnk }} = {% include "foobar.sql" %}
  )
{% if +level - -level + level.level + level + level["key"] >= 0 %}
where rnk = 1
{% endif %}
