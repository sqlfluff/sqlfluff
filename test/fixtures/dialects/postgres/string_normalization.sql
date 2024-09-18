SELECT (test_column IS NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NFC NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NFD NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NFKC NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NFKD NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NOT NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NOT NFC NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NOT NFD NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NOT NFKC NORMALIZED) AS is_normalized FROM test_table;
SELECT (test_column IS NOT NFKD NORMALIZED) AS is_normalized FROM test_table;

CREATE DOMAIN text_default AS TEXT CHECK (VALUE IS NORMALIZED);
CREATE DOMAIN text_nfc AS TEXT CHECK (VALUE IS NFC NORMALIZED);
CREATE DOMAIN text_nfd AS TEXT CHECK (VALUE IS NFD NORMALIZED);
CREATE DOMAIN text_nfkc AS TEXT CHECK (VALUE IS NFKC NORMALIZED);
CREATE DOMAIN text_nfkd AS TEXT CHECK (VALUE IS NFKD NORMALIZED);
CREATE DOMAIN text_default AS TEXT CHECK (VALUE IS NOT normalized);
CREATE DOMAIN text_nfc AS TEXT CHECK (VALUE IS NOT NFC NORMALIZED);
CREATE DOMAIN text_nfd AS TEXT CHECK (VALUE IS NOT NFD NORMALIZED);
CREATE DOMAIN text_nfkc AS TEXT CHECK (VALUE IS NOT NFKC NORMALIZED);
CREATE DOMAIN text_nfkd AS TEXT CHECK (VALUE IS NOT NFKD NORMALIZED);


create table test_table (
    test_column text primary key,
    CONSTRAINT default_constraint CHECK (test_column IS NORMALIZED),
    CONSTRAINT nfc_constraint CHECK (test_column IS NFC NORMALIZED),
    CONSTRAINT nfd_constraint CHECK (test_column IS NFD NORMALIZED),
    CONSTRAINT nfkc_constraint CHECK (test_column IS NFKC NORMALIZED),
    CONSTRAINT nfkd_constraint CHECK (test_column IS NFKD NORMALIZED),
    CONSTRAINT not_default_constraint CHECK (test_column IS NOT NORMALIZED),
    CONSTRAINT not_nfc_constraint CHECK (test_column IS NOT NFC NORMALIZED),
    CONSTRAINT not_nfd_constraint CHECK (test_column IS NOT NFD NORMALIZED),
    CONSTRAINT not_nfkc_constraint CHECK (test_column IS NOT NFKC NORMALIZED),
    CONSTRAINT not_nfkd_constraint CHECK (test_column IS NOT NFKD NORMALIZED)
);
