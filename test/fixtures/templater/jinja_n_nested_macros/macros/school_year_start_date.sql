{% from 'week_start_date.sql' import week_start_date  %}
{% macro school_year_start_date( date ) %}

-- Each new school year starts at the beginning of the week July 1 falls in:
date_trunc( 'week',
  TO_DATE( '01 July' ||

  -- If date is on or after this calendar year's school year start,
  -- then date is in the school year that started this calendar year
  case when
    TO_DATE( '01 July' ||
      extract(year from {{ week_start_date( date ) }})
	, 'DD Mon YYYY' )
    <= CONVERT_TIMEZONE( 'UTC', 'America/New_York',  {{date}} )

  then extract(year from {{ week_start_date( date ) }} )

  -- Otherwise, school year started in previous calendar year
  else extract(year from {{ week_start_date( date ) }} )  - 1

  end
  , 'DD Mon YYYY' )

)

{% endmacro %}
