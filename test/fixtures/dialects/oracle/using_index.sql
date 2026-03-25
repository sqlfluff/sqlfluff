-- Form 1: Named index reference

CREATE TABLE t_pk_named_idx (
    id NUMBER,
    CONSTRAINT pk_t_pk_named_idx PRIMARY KEY (id)
        USING INDEX pk_t_pk_named_idx_idx
);

CREATE TABLE t_uq_named_idx (
    code VARCHAR2(10),
    CONSTRAINT uq_t_uq_named_idx UNIQUE (code)
        USING INDEX myschema.uq_t_uq_named_idx_idx
);

-- Form 2: Physical attributes (no inline DDL, no index name)

CREATE TABLE t_pk_pctfree (
    id NUMBER,
    CONSTRAINT pk_t_pk_pctfree PRIMARY KEY (id)
        USING INDEX PCTFREE 10
);

CREATE TABLE t_pk_tablespace (
    id NUMBER,
    CONSTRAINT pk_t_pk_tablespace PRIMARY KEY (id)
        USING INDEX TABLESPACE idx_ts
);

CREATE TABLE t_uq_nologging (
    code VARCHAR2(10),
    CONSTRAINT uq_t_uq_nologging UNIQUE (code)
        USING INDEX NOLOGGING
);

CREATE TABLE t_pk_multi_attrs (
    id NUMBER,
    CONSTRAINT pk_t_pk_multi_attrs PRIMARY KEY (id)
        USING INDEX
            PCTFREE 10
            INITRANS 2
            TABLESPACE idx_ts
            NOLOGGING
);

CREATE TABLE t_pk_storage (
    id NUMBER,
    CONSTRAINT pk_t_pk_storage PRIMARY KEY (id)
        USING INDEX
            PCTFREE 10
            TABLESPACE idx_ts
            STORAGE (INITIAL 140K NEXT 360K BUFFER_POOL KEEP)
            NOLOGGING
);

CREATE TABLE t_uq_parallel (
    code VARCHAR2(10),
    CONSTRAINT uq_t_uq_parallel UNIQUE (code)
        USING INDEX PARALLEL 4
);

CREATE TABLE t_pk_compress (
    id NUMBER,
    col2 VARCHAR2(20),
    CONSTRAINT pk_t_pk_compress PRIMARY KEY (id, col2)
        USING INDEX COMPRESS 1
);

CREATE TABLE t_pk_invisible (
    id NUMBER,
    CONSTRAINT pk_t_pk_invisible PRIMARY KEY (id)
        USING INDEX INVISIBLE
);

CREATE TABLE t_pk_reverse (
    id NUMBER,
    CONSTRAINT pk_t_pk_reverse PRIMARY KEY (id)
        USING INDEX REVERSE
);

-- Form 3: Inline CREATE INDEX

CREATE TABLE t_pk_inline_idx (
    id NUMBER,
    CONSTRAINT pk_t_pk_inline_idx PRIMARY KEY (id)
        USING INDEX (CREATE INDEX pk_t_pk_inline_idx_i ON t_pk_inline_idx (id))
);

CREATE TABLE t_pk_inline_unique_idx (
    id NUMBER,
    CONSTRAINT pk_t_pk_inline_unique_idx PRIMARY KEY (id)
        USING INDEX (
            CREATE UNIQUE INDEX pk_t_pk_inline_unique_idx_i
                ON t_pk_inline_unique_idx (id)
        )
);

CREATE TABLE t_uq_inline_idx (
    code VARCHAR2(10),
    CONSTRAINT uq_t_uq_inline_idx UNIQUE (code)
        USING INDEX (CREATE INDEX uq_t_uq_inline_idx_i ON t_uq_inline_idx (code))
);

CREATE TABLE t_uq_inline_bitmap_idx (
    status NUMBER,
    CONSTRAINT uq_t_uq_inline_bitmap_idx UNIQUE (status)
        USING INDEX (
            CREATE BITMAP INDEX uq_t_uq_inline_bitmap_idx_i
                ON t_uq_inline_bitmap_idx (status)
        )
);

CREATE TABLE t_pk_inline_ts (
    id NUMBER,
    CONSTRAINT pk_t_pk_inline_ts PRIMARY KEY (id)
        USING INDEX (
            CREATE INDEX pk_t_pk_inline_ts_i ON t_pk_inline_ts (id)
            TABLESPACE idx_ts
        )
);

CREATE TABLE t_pk_inline_attrs (
    id NUMBER,
    CONSTRAINT pk_t_pk_inline_attrs PRIMARY KEY (id)
        USING INDEX (
            CREATE INDEX pk_t_pk_inline_attrs_i ON t_pk_inline_attrs (id)
            TABLESPACE idx_ts
            PCTFREE 10
            INITRANS 2
            NOLOGGING
        )
);

CREATE TABLE t_pk_inline_storage (
    id NUMBER,
    CONSTRAINT pk_t_pk_inline_storage PRIMARY KEY (id)
        USING INDEX (
            CREATE INDEX pk_t_pk_inline_storage_i ON t_pk_inline_storage (id)
            TABLESPACE idx_ts
            STORAGE (
                INITIAL 256K
                NEXT 256K
                MINEXTENTS 1
                MAXEXTENTS UNLIMITED
                BUFFER_POOL DEFAULT
            )
            NOLOGGING
        )
);

CREATE TABLE t_uq_inline_full (
    code VARCHAR2(20),
    name VARCHAR2(100),
    CONSTRAINT uq_t_uq_inline_full UNIQUE (code, name)
        USING INDEX (
            CREATE UNIQUE INDEX uq_t_uq_inline_full_i ON t_uq_inline_full (code, name)
            TABLESPACE idx_ts
            PCTFREE 5
            INITRANS 4
            NOLOGGING
            PARALLEL 2
            COMPRESS 1
            VISIBLE
        )
);

-- Multiple constraints in the same table, each with a different USING INDEX form

CREATE TABLE t_multi_constraints (
    id      NUMBER,
    code    VARCHAR2(10),
    status  NUMBER,
    -- Named index reference
    CONSTRAINT pk_t_multi_constraints PRIMARY KEY (id)
        USING INDEX pk_t_multi_constraints_idx,
    -- Physical attributes
    CONSTRAINT uq_t_multi_constraints_code UNIQUE (code)
        USING INDEX TABLESPACE idx_ts NOLOGGING,
    -- Inline CREATE INDEX
    CONSTRAINT uq_t_multi_constraints_status UNIQUE (status)
        USING INDEX (
            CREATE INDEX uq_t_multi_constraints_status_i
                ON t_multi_constraints (status)
            TABLESPACE idx_ts
        )
);

-- Without explicit CONSTRAINT name (anonymous constraint)

CREATE TABLE t_anon_pk_inline (
    id NUMBER,
    PRIMARY KEY (id)
        USING INDEX (CREATE INDEX anon_pk_inline_i ON t_anon_pk_inline (id))
);

CREATE TABLE t_anon_uq_attrs (
    code VARCHAR2(10),
    UNIQUE (code) USING INDEX PCTFREE 10 TABLESPACE idx_ts
);
