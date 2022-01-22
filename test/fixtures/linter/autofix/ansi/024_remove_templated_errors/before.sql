-- Templated query aimed to test the BaseRule.remove_templated_errors()
-- function's behavior of not modifying templated sections.
SELECT
   {{ par_wrap() }}
  , line_two as line_two
