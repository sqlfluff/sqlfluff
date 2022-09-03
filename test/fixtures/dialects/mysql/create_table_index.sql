CREATE TABLE foo (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  a TEXT(500),
  b INT,
  PRIMARY KEY (id) COMMENT 'primary key (id)',
  FULLTEXT `idx_a` (a) COMMENT 'index (a)',
  INDEX `idx_b` (b) COMMENT 'index (b)'
) ENGINE=InnoDB;
