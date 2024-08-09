-- materialization is a custom jinja tag, testing that the templater does not error
{% materialization my_materialization_name, default %}
 -- materialization...
{% endmaterialization %}
