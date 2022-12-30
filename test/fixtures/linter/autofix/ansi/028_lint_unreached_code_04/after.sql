SELECT
    c1,
    c2
FROM fori WHERE
    1 = 1
    {% if False %}
        AND today() >= dateadd(DAY, -31, {{ '2017/08/25' }})
        AND fori.delivered_date_pt < '{{ '2020/08/01' }}'
    {% endif %}
