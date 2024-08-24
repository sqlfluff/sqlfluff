CREATE TABLE parent (
    id INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE child (
    id INT,
    parent_id INT,
    INDEX par_ind (parent_id),
    FOREIGN KEY (parent_id)
        REFERENCES parent(id)
        ON DELETE CASCADE
);

CREATE TABLE product (
    category INT NOT NULL, id INT NOT NULL,
    price DECIMAL,
    PRIMARY KEY(category, id)
);

CREATE TABLE customer (
    id INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE product_order (
    product_category INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,

    PRIMARY KEY(no),
    -- INDEX (product_category, product_id),
    -- INDEX (customer_id),

    FOREIGN KEY (product_category, product_id)
      REFERENCES product(category, id)
      ON UPDATE CASCADE ON DELETE RESTRICT,

    FOREIGN KEY (customer_id)
      REFERENCES customer(id)
);

CREATE TABLE source_tag_assoc (
    source_id INT UNSIGNED NOT NULL,
    tag_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (source_id, tag_id),
    FOREIGN KEY (source_id) REFERENCES source (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES source_tag (id) ON DELETE CASCADE
);
