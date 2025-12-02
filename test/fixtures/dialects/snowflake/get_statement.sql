get @%mytable file://C:\temp\load;
get @~/myfiles file:///tmp/data/;
get @~/myfiles file:///tmp/data/ PATTERN = '.*foo.*';
get @~/myfiles file:///tmp/data/ PATTERN = $foo;
get @~/myfiles file:///tmp/data/ PARALLEL = 1;
