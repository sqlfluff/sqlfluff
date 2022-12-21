CREATE TABLE a(
    a INT NOT NULL,
    UNIQUE (a),
    UNIQUE idx_c(a),
    UNIQUE KEY (a),
    UNIQUE KEY idx_a(a),
    UNIQUE INDEX (a),
    UNIQUE INDEX idx_b(a)
)
