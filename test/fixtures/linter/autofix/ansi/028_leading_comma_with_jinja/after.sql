{% set isENTER = true %}
SELECT
    myt.c1
    {% if isENTER %}
        , myt.c2
    {% endif %}
    , myt.dt,
    coalesce(myt.c3, 0) as c3,
    coalesce(myt.c4, 0) as c4
from myt
