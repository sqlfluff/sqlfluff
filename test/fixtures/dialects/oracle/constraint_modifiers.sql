-- Table-level ENABLE
CREATE TABLE t_state_enable (
    id NUMBER,
    CONSTRAINT ck_state_enable CHECK (id > 0) ENABLE
);

-- Inline DISABLE
CREATE TABLE t_state_disable (
    id NUMBER CONSTRAINT ck_state_disable CHECK (id > 0) DISABLE
);

-- Table-level VALIDATE
CREATE TABLE t_state_validate (
    id NUMBER,
    CONSTRAINT ck_state_validate CHECK (id > 0) VALIDATE
);

-- Inline NOVALIDATE
CREATE TABLE t_state_novalidate (
    id NUMBER CONSTRAINT ck_state_novalidate CHECK (id > 0) NOVALIDATE
);

-- Table-level RELY
CREATE TABLE t_state_rely (
    code VARCHAR2(20),
    CONSTRAINT uq_state_rely UNIQUE (code) RELY
);

-- Inline NORELY
CREATE TABLE t_state_norely (
    code VARCHAR2(20) CONSTRAINT uq_state_norely UNIQUE NORELY
);

-- Table-level DEFERRABLE
CREATE TABLE t_state_deferrable (
    id NUMBER,
    CONSTRAINT pk_state_deferrable PRIMARY KEY (id) DEFERRABLE
);

-- Inline NOT DEFERRABLE
CREATE TABLE t_state_not_deferrable (
    id NUMBER CONSTRAINT pk_state_not_deferrable PRIMARY KEY NOT DEFERRABLE
);

-- Inline NOT NULL NOVALIDATE
CREATE TABLE t_state_not_null_novalidate (
    id NUMBER CONSTRAINT nn_state_novalidate NOT NULL NOVALIDATE
);

-- Inline NOT NULL RELY
CREATE TABLE t_state_not_null_rely (
    id NUMBER CONSTRAINT nn_state_rely NOT NULL RELY
);

-- Inline NOT NULL DEFERRABLE
CREATE TABLE t_state_not_null_deferrable (
    id NUMBER CONSTRAINT nn_state_deferrable NOT NULL DEFERRABLE
);

-- Table-level INITIALLY IMMEDIATE
CREATE TABLE t_state_initially_immediate (
    id NUMBER,
    CONSTRAINT pk_state_initially_immediate PRIMARY KEY (id)
        DEFERRABLE INITIALLY IMMEDIATE
);

-- Inline INITIALLY DEFERRED
CREATE TABLE t_state_initially_deferred (
    id NUMBER CONSTRAINT pk_state_initially_deferred PRIMARY KEY
        DEFERRABLE INITIALLY DEFERRED
);

-- INITIALLY may precede DEFERRABLE
CREATE TABLE t_state_initially_first (
    id NUMBER,
    CONSTRAINT pk_state_initially_first PRIMARY KEY (id)
        INITIALLY DEFERRED DEFERRABLE
);

-- Table-level ordered composition with USING INDEX
CREATE TABLE t_state_table_composed (
    id NUMBER,
    CONSTRAINT pk_state_table_composed PRIMARY KEY (id)
        USING INDEX TABLESPACE idx_ts
        DEFERRABLE INITIALLY DEFERRED RELY ENABLE NOVALIDATE
);

-- Inline ordered composition with USING INDEX
CREATE TABLE t_state_inline_composed (
    code VARCHAR2(20) CONSTRAINT uq_state_inline_composed UNIQUE
        USING INDEX TABLESPACE idx_ts
        NOT DEFERRABLE NORELY DISABLE NOVALIDATE
);
