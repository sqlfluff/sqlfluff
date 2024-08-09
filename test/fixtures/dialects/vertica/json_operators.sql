select
    mapjsonextractor('{"data":' || col || '}' using parameters flatten_maps=false) as mapped
from prepared
