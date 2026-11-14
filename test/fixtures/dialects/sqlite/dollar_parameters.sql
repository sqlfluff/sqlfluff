SELECT $name, $name(suffix), $name();
SELECT $ns::value, $ns::nested::value(suffix);
SELECT $ns::value(key.with-punctuation), $ns::value(key,other);
SELECT $name::, $name::(suffix);
SELECT $ns::value + 1, $name(suffix) || ' text';
SELECT * FROM items WHERE id = $app::item(id);
SELECT $::name, $::::name, $::ns::value(suffix);
SELECT $name$value, $$name, $::name$(suffix);
