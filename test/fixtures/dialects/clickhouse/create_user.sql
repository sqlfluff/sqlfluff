-- This file tests CREATE USER with/without IDENTIFIED BY for ClickHouse dialect
-- sqlfluff:dialect:clickhouse

CREATE USER new_user IDENTIFIED BY 'secret';
CREATE USER another_user IDENTIFIED WITH sha256_password BY 'hash';

CREATE USER yet_another_user;
