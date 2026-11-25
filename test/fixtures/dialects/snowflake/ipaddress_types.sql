CREATE TABLE sample_ipaddress_table (ip_col IPADDRESS);

SELECT
    ip_col::IPADDRESS AS ip1,
    CAST(ip_col AS IPADDRESS) AS ip2,
    TRY_CAST(ip_col AS IPADDRESS) AS ip3
FROM sample_ipaddress_table;

SELECT IPADDRESS '2001:db8::1' AS ip;
