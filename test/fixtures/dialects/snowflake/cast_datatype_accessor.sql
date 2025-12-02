SELECT bar::array[0] AS channel
    , foo:bar::array[2] AS channel2
    , bar::array[0][1] AS channel3
    , raw:foo::array[0]::string AS channel4
FROM my_table;

SELECT
    foo::variant:field::array[0]::string AS name
FROM my_table;

SELECT DISTINCT
    payload::variant::object:name::text AS name,
    payload::variant::object AS details,
    payload::variant::object:createdAt::timestamp_ntz AS created,
    payload::variant::object:updatedAt::timestamp_ntz AS updated,
    payload::variant::object:id::number AS id
FROM raw_source_table
