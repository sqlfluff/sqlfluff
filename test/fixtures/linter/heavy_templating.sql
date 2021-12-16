{%
    set properties = {
        "id": "id",
        "type": "post_type",
        "channel_id": "episode_id"
    }
%}

select
    {% for prop, col in properties.items() %}
        {% if not loop.first %} , {% endif %}
            {{prop}} as {{ col}}
    {% endfor %}
from {{ ref("snowplow_events_dev") }}
