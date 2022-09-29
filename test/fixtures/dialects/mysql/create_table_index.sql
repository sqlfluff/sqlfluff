CREATE TABLE foo (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  a TEXT(500),
  b INT,
  c INT,
  PRIMARY KEY (id) COMMENT 'primary key (id)',
  FULLTEXT `idx_a` (a) COMMENT 'index (a)',
  INDEX `idx_prefix_a` (a(20)),
  INDEX `idx_b` (b) COMMENT 'index (b)',
  INDEX `idx_desc_b` (b DESC),
  INDEX `idx_asc_c` (c ASC)
) ENGINE=InnoDB;
