{#
This calculates the distance between two sets of latitude and longitude.
The formula is from the following blog post:
http://daynebatten.com/2015/09/latitude-longitude-distance-sql/

The arguments should be float type. 
#}

{% macro haversine_distance(lat1,lon1,lat2,lon2) -%}

    2 * 3961 * asin(sqrt((sin(radians(({{lat2}} - {{lat1}}) / 2))) ^ 2 +
    cos(radians({{lat1}})) * cos(radians({{lat2}})) *
    (sin(radians(({{lon2}} - {{lon1}}) / 2))) ^ 2))

{%- endmacro %}
