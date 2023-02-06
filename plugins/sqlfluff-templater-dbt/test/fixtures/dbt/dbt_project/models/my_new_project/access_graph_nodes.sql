-- Verify that the dbt context variable graph is accessible
{% set graph_node = graph.nodes.values() | selectattr('name', 'equalto', 'fact_product_contract_values') | first -%}
{%- set num_parents = graph_node.depends_on.nodes | length -%}

select {{ num_parents }} as number_of_parents
