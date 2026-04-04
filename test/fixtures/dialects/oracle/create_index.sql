CREATE INDEX s1.t_basic_idx ON s1.t (col1);

CREATE INDEX s1.t_multi_idx ON s1.t (col1, col2, col3);

CREATE UNIQUE INDEX s1.t_unique_idx ON s1.t (col1, col2);

CREATE BITMAP INDEX s1.t_bitmap_idx ON s1.t (status_col);

CREATE INDEX s1.t_schema_idx ON s1.t (col1);

CREATE INDEX s1.t_ts_idx ON s1.t (col1)

TABLESPACE idx_ts;

-- Physical attributes
CREATE INDEX s1.t_pct_idx ON s1.t (col1)
PCTFREE 10
INITRANS 2
MAXTRANS 255
TABLESPACE idx_ts;

CREATE INDEX s1.t_storage_idx ON s1.t (col1)
TABLESPACE idx_ts
STORAGE (
    INITIAL 256K
    NEXT 256K
    MINEXTENTS 1
    MAXEXTENTS UNLIMITED
    PCTINCREASE 0
    FREELISTS 1
    FREELIST GROUPS 1
    BUFFER_POOL DEFAULT
);

CREATE INDEX s1.t_storage_keep_idx ON s1.t (col1)
TABLESPACE idx_ts
STORAGE (
    INITIAL 512K
    NEXT 512K
    MAXEXTENTS UNLIMITED
    BUFFER_POOL KEEP
);

CREATE INDEX s1.t_storage_recycle_idx ON s1.t (col1)
TABLESPACE idx_ts
STORAGE (
    INITIAL 128K
    NEXT 128K
    MAXEXTENTS 500
    BUFFER_POOL RECYCLE
);

-- Logging / redo
CREATE INDEX s1.t_logging_idx ON s1.t (col1)
TABLESPACE idx_ts
LOGGING;

CREATE INDEX s1.t_nologging_idx ON s1.t (col1)
TABLESPACE idx_ts
NOLOGGING;

-- Parallelism: PARALLEL degree and NOPARALLEL
CREATE INDEX s1.t_parallel_idx ON s1.t (col1)
TABLESPACE idx_ts
PARALLEL 4;

CREATE INDEX s1.t_parallel_default_idx ON s1.t (col1)
TABLESPACE idx_ts
PARALLEL;

CREATE INDEX s1.t_noparallel_idx ON s1.t (col1)
TABLESPACE idx_ts
NOPARALLEL;

-- ONLINE index build
CREATE INDEX s1.t_online_idx ON s1.t (col1)
TABLESPACE idx_ts
ONLINE;

-- Bare COMPRESS (uses default prefix length)
CREATE INDEX s1.t_compress_idx ON s1.t (col1, col2)
TABLESPACE idx_ts
COMPRESS;

-- COMPRESS with integer: compress first n leading key columns
CREATE INDEX s1.t_compress_1_idx ON s1.t (col1, col2, col3)
TABLESPACE idx_ts
COMPRESS 1;

-- COMPRESS 2 on composite unique index
CREATE UNIQUE INDEX s1.t_compress_2_unique_idx ON s1.t (col1, col2, col3)
TABLESPACE idx_ts
COMPRESS 2;

CREATE INDEX s1.t_nocompress_idx ON s1.t (col1)
TABLESPACE idx_ts
NOCOMPRESS;

-- REVERSE key index
CREATE INDEX s1.t_reverse_idx ON s1.t (col1)
TABLESPACE idx_ts
REVERSE;

-- VISIBLE / INVISIBLE
CREATE INDEX s1.t_visible_idx ON s1.t (col1)
TABLESPACE idx_ts
VISIBLE;

CREATE INDEX s1.t_invisible_idx ON s1.t (col1)
TABLESPACE idx_ts
INVISIBLE;

-- Ascending / descending column order
CREATE INDEX s1.t_asc_desc_idx ON s1.t (col1 ASC, col2 DESC, col3 ASC);

-- NOLOGGING + full STORAGE + PARALLEL combined
CREATE INDEX s1.t_full_phys_idx
    ON s1.t (col1, col2)
TABLESPACE idx_ts
NOLOGGING
PCTFREE 10
INITRANS 2
MAXTRANS 255
STORAGE (
    INITIAL 655K
    NEXT 655K
    MINEXTENTS 1
    MAXEXTENTS UNLIMITED
    PCTINCREASE 50
    FREELISTS 1
    FREELIST GROUPS 1
    BUFFER_POOL DEFAULT
)
PARALLEL 8
NOCOMPRESS
VISIBLE;

-- Other
CREATE INDEX s1.t_nosort_idx ON s1.t (col1)
TABLESPACE idx_ts
NOSORT;

CREATE INDEX s1.t_nosort_attrs_idx ON s1.t (col1, col2)
TABLESPACE idx_ts
PCTFREE 10
INITRANS 2
NOLOGGING
NOSORT;

CREATE INDEX s1.t_reverse_attrs_idx ON s1.t (col1)
TABLESPACE idx_ts
PCTFREE 10
NOLOGGING
REVERSE;

-- Comprehensive examples
CREATE INDEX s1.log_instdati_idx
    ON s1.log (institution_id, datetime)
PCTFREE 10
INITRANS 2
MAXTRANS 255
TABLESPACE idx_ts
STORAGE (
    INITIAL 655K
    NEXT 655K
    MINEXTENTS 1
    MAXEXTENTS UNLIMITED
    PCTINCREASE 50
    FREELISTS 1
    FREELIST GROUPS 1
    BUFFER_POOL DEFAULT
)
NOLOGGING
NOPARALLEL;

CREATE UNIQUE INDEX s1.filter_instkeytype_idx
    ON s1.filter (institution_id, filterkey, filtertype_id)
PCTFREE 10
INITRANS 2
MAXTRANS 255
TABLESPACE idx_ts
STORAGE (
    INITIAL 140K
    NEXT 360K
    MINEXTENTS 1
    MAXEXTENTS UNLIMITED
    PCTINCREASE 50
    FREELISTS 1
    FREELIST GROUPS 1
    BUFFER_POOL DEFAULT
)
NOLOGGING
PARALLEL 4;
