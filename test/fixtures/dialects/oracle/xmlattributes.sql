-- XMLELEMENT with a nested XMLATTRIBUTES clause. The attribute values take an
-- optional alias, which the generic function contents grammar rejects.
-- https://github.com/sqlfluff/sqlfluff/issues/8112
select
   xmlelement(
      "xml_el"
      , xmlattributes (
         'attr1' as "attr_name1"
        ,'attr2' as "attr_name2"
      )
   )
from ex_tab;

-- The AS keyword is optional and the value can be any expression.
select
   xmlelement(
      "rec"
      , xmlattributes(id as "id", first_name || ' ' || last_name full_name)
   )
from employees;
