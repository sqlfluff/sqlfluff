CREATE TABLE t3 (
	a VARCHAR(255) NOT NULL,
	b VARCHAR(255) NOT NULL,
	c INT8 NOT NULL,
	CONSTRAINT fkmj1gk1jugvhbvivigv58p484n FOREIGN KEY (c) REFERENCES t4 (a),
	UNIQUE INDEX ukihbvfdx2sepbue138k3klttaa4 (c ASC),
	CONSTRAINT fkc5ckayrrihbvfdxveirrgtlwo FOREIGN KEY (a, b) REFERENCES t5 (a, b),
	INDEX i99 (a ASC, b ASC)
);
