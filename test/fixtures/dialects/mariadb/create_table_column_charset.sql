CREATE TABLE t1
(
    col1 VARCHAR(5)
      CHARACTER SET latin1
      COLLATE latin1_german1_ci
);

CREATE TABLE t1
(
    col1 VARCHAR(5)
      CHARACTER SET `latin1`
      COLLATE `latin1_german1_ci`
);

CREATE TABLE t1
(
    col1 VARCHAR(5)
      CHARACTER SET 'latin1'
      COLLATE 'latin1_german1_ci'
);

CREATE TABLE t1
(
    col1 VARCHAR(5)
      CHARACTER SET "latin1"
      COLLATE "latin1_german1_ci"
);

-- Keyword charset name (ascii is an unreserved keyword): must parse as a
-- character_set, not a naked_identifier, so rule RF04 does not flag it.
CREATE TABLE t2
(
    col1 TEXT CHARACTER SET ascii COLLATE ascii_bin
);

-- The reserved keyword BINARY is a valid charset name and collation name.
CREATE TABLE t3
(
    col1 TEXT CHARACTER SET binary,
    col2 TEXT COLLATE binary
);
