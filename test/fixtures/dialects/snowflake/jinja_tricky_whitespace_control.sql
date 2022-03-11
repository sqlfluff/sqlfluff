-- Added for issue 2786. This file originally failed to parse due to invalid slice
-- output from JinjaTracer.
{{
    config(
        materialized='incremental',
        unique_key='md5_surrogate_key_main'
    )
}}

{%- set first_list = ["value1", "value2", "value3"] -%}
{%- set second_list = ["value4", "value5", "value6"] -%}
{%- set third_list = ["value7", "value8", "value9"] -%}

with fill_na_values as (
    select
        id,
        run_date,
        md5_surrogate_key_main,
        {%- for features in second_list %}
            {%- if features in third_list %}
                coalesce({{features}}, (select feature_mode from {{ ref('second_list') }} where features = '{{features}}')) as {{features}}
                {%- if not loop.last -%},{% endif %}
            {%- else -%}
                coalesce({{features}}, (select feature_mean from {{ ref('second_list') }} where features = '{{features}}')) as {{features}}
                {%- if not loop.last -%},{% endif %}
            {%- endif -%}
        {%- endfor %}
    from {{ ref('training_dataset') }}
    {%- if is_incremental() %}
    where current_date >= (select max(run_date) from {{ this }})
    {%- else %}
    where run_date >= '2021-01-01'
    {%- endif %}
),

winsorize_data as (
    select
        md5_surrogate_key_main,
        {%- for features in second_list %}
            {%- if features in first_list %}
                case
                    when {{features}} < (select fifth_percentile from {{ ref('first_list') }} where winsorize_column = '{{features}}')
                    then (select fifth_percentile from {{ ref('first_list') }} where winsorize_column = '{{features}}')
                    when {{features}} > (select ninetyfifth_percentile from {{ ref('first_list') }} where winsorize_column = '{{features}}')
                    then (select ninetyfifth_percentile from {{ ref('first_list') }} where winsorize_column = '{{features}}')
                    else {{features}}
                end as {{features}}
                {%- if not loop.last -%},{% endif %}
            {%- else %}
                {{features}}
                {%- if not loop.last -%},{% endif %}
            {%- endif %}
        {%- endfor %}
    from fill_na_values
),

scaling_data as (
    select
        md5_surrogate_key_main,
        {%- for features in second_list %}
            ({{features}} - (select feature_mean from {{ ref('second_list') }} where features = '{{features}}'))/(select feature_std from {{ ref('second_list') }} where features = '{{features}}') as {{features}}
            {%- if not loop.last -%},{% endif %}
        {%- endfor %}
    from winsorize_data
),

apply_ceofficients as (
    select
        md5_surrogate_key_main,
        {%- for features in second_list %}
            {{features}} * (select coefficients from {{ ref('second_list') }} where features = '{{features}}') as {{features}}_coef
            {%- if not loop.last -%},{% endif %}
        {%- endfor %}
    from scaling_data
),

logistic_prediction as (
    select
        fan.*,
        1/(1+EXP(-(0.24602303+coef1+coef2+coef3+coef4+coef5+coef6+coef7+coef8+coef9+available_balance_coef+coef10+coef11+coef12+coef13+coef14))) as prediction_probability,
        case when prediction_probability < .5 then 0 else 1 end as prediction_class
    from apply_ceofficients ac
    inner join fill_na_values fan
        on ac.md5_surrogate_key_main = fan.md5_surrogate_key_main
)

select * from logistic_prediction

