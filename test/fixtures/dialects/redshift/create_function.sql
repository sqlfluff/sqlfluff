CREATE OR REPLACE FUNCTION public.iif(
    condition BOOLEAN
    , true_result ANYELEMENT
    , false_result ANYELEMENT) RETURNS ANYELEMENT
STABLE
AS
$$
    if condition:
        return true_result
    return false_result
$$
LANGUAGE plpythonu;
