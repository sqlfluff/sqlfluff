SELECT bar::array[0] AS channel
    , foo:bar::array[2] AS channel2
    , bar::array[0][1] AS channel3
    , raw:foo::array[0]::string AS channel4
FROM my_table;
