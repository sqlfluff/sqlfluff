ALTER TABLE distributors ADD COLUMN address varchar(30);

ALTER TABLE measurements
  ADD COLUMN mtime timestamp with time zone DEFAULT now();

ALTER TABLE transactions
  ADD COLUMN status varchar(30) DEFAULT 'old',
  ALTER COLUMN status SET default 'current';

ALTER TABLE distributors DROP COLUMN address RESTRICT;

ALTER TABLE distributors
    ALTER COLUMN address TYPE varchar(80),
    ALTER COLUMN name TYPE varchar(100);

ALTER TABLE foo
    ALTER COLUMN foo_timestamp SET DATA TYPE timestamp with time zone
    USING
        timestamp with time zone 'epoch' + foo_timestamp * interval '1 second';

ALTER TABLE foo
    ALTER COLUMN foo_timestamp DROP DEFAULT,
    ALTER COLUMN foo_timestamp TYPE timestamp with time zone
    USING
        timestamp 'epoch' + foo_timestamp * interval '1 second',
    ALTER COLUMN foo_timestamp SET DEFAULT now();

ALTER TABLE mytable ALTER date_column SET DEFAULT NOW();
ALTER TABLE mytable ALTER int_column SET DEFAULT 1;
ALTER TABLE mytable ALTER text_column SET DEFAULT 'value';
ALTER TABLE mytable ALTER bool_column SET DEFAULT false;
ALTER TABLE mytable ALTER other_column SET DEFAULT other_value;
ALTER TABLE mytable ALTER other_column SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE mytable ALTER other_column SET DEFAULT a_function(a_parameter);
ALTER TABLE mytable ALTER other_column SET DEFAULT a_function('a_parameter');
ALTER TABLE mytable ALTER other_column SET DEFAULT 1 + 2 + 3;
ALTER TABLE mytable ALTER other_column SET DEFAULT (1 + 2 + 3);
ALTER TABLE mytable ALTER other_column DROP DEFAULT;
ALTER TABLE IF EXISTS mytable ALTER date_column SET DEFAULT NOW();
ALTER TABLE IF EXISTS mytable ALTER int_column SET DEFAULT 1;
ALTER TABLE IF EXISTS mytable ALTER text_column SET DEFAULT 'value';
ALTER TABLE IF EXISTS mytable ALTER bool_column SET DEFAULT false;
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT other_value;
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT a_function(a_parameter);
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT a_function('a_parameter');
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT 1 + 2 + 3;
ALTER TABLE IF EXISTS mytable ALTER other_column SET DEFAULT (1 + 2 + 3);
ALTER TABLE IF EXISTS mytable ALTER other_column DROP DEFAULT;

ALTER TABLE distributors RENAME COLUMN address TO city;

ALTER TABLE distributors RENAME TO suppliers;

ALTER TABLE distributors RENAME CONSTRAINT zipchk TO zip_check;

ALTER TABLE distributors ALTER COLUMN street SET NOT NULL;

ALTER TABLE distributors ALTER COLUMN street DROP NOT NULL;

ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);

ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5) NO INHERIT;

ALTER TABLE distributors DROP CONSTRAINT zipchk;

-- constraints can optionally have their names double-quoted
ALTER TABLE distributors DROP CONSTRAINT "zipchk";

ALTER TABLE ONLY distributors DROP CONSTRAINT zipchk;

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address);

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address) MATCH FULL;

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address) NOT VALID;

ALTER TABLE distributors VALIDATE CONSTRAINT distfk;

ALTER TABLE distributors ADD CONSTRAINT dist_id_zipcode_key UNIQUE (dist_id, zipcode);

ALTER TABLE distributors ADD PRIMARY KEY (dist_id);

ALTER TABLE distributors SET TABLESPACE fasttablespace;

-- Issue:2071
ALTER TABLE distributors SET (parameter_1 = 'value');

ALTER TABLE distributors SET (parameter_1 = 1);

ALTER TABLE distributors SET (parameter_1 = 1, parameter_2 = 'value');

ALTER TABLE myschema.distributors SET SCHEMA yourschema;

ALTER TABLE distributors DROP CONSTRAINT distributors_pkey,
    ADD CONSTRAINT distributors_pkey PRIMARY KEY USING INDEX dist_id_temp_idx;

ALTER TABLE measurement
    ATTACH PARTITION measurement_y2016m07 FOR VALUES FROM ('2016-07-01') TO ('2016-08-01');

ALTER TABLE cities
    ATTACH PARTITION cities_ab FOR VALUES IN ('a', 'b');

ALTER TABLE orders
    ATTACH PARTITION orders_p4 FOR VALUES WITH (MODULUS 4, REMAINDER 3);

ALTER TABLE cities
    ATTACH PARTITION cities_partdef DEFAULT;

ALTER TABLE measurement
    DETACH PARTITION measurement_y2015m12;

ALTER TABLE measurement
    DETACH PARTITION measurement_y2021m10 CONCURRENTLY FINALIZE;

ALTER TABLE landing.workorderhistory
ADD CONSTRAINT workorder_id_foreign_key
FOREIGN KEY(workorderid) REFERENCES landing.workorder(id);

ALTER TABLE my_table ADD COLUMN IF NOT EXISTS foo TEXT;

ALTER TABLE public.obm_buildings
OWNER to postgres;

ALTER TABLE distributors ALTER COLUMN street ADD GENERATED ALWAYS AS IDENTITY (INCREMENT 4 NO MAXVALUE);

ALTER TABLE distributors ALTER COLUMN street SET RESTART WITH 3;

ALTER TABLE distributors ADD my_column int GENERATED BY DEFAULT AS IDENTITY (CACHE 3 MAXVALUE 63 OWNED BY NONE);

ALTER TABLE public.test OWNER TO "ID";

ALTER TABLE public.test OWNER TO ID;

ALTER TABLE IF EXISTS ONLY public.test OWNER TO CURRENT_ROLE;

ALTER TABLE public.history ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.history_id_seq
);

-- Test adding columns with UNIQUE and PRIMARY KEY constraints

ALTER TABLE tbl
    ADD COLUMN nulls_distinct text UNIQUE NULLS DISTINCT,
    ADD COLUMN nulls_not_distinct text UNIQUE NULLS NOT DISTINCT,
    ADD everything text UNIQUE NULLS DISTINCT WITH (arg1=3, arg5='str') USING INDEX TABLESPACE spc;

ALTER TABLE tbl
    ADD pk text
        DEFAULT 'hello'
        PRIMARY KEY WITH (arg1=3, arg5='str') USING INDEX TABLESPACE tblspace NOT NULL;

ALTER TABLE tbl
    ADD CONSTRAINT foo1 UNIQUE (fld, col),
    ADD CONSTRAINT foo2 UNIQUE NULLS DISTINCT (fld),
    ADD CONSTRAINT foo3 UNIQUE NULLS NOT DISTINCT (fld),
    ADD CONSTRAINT everything UNIQUE NULLS DISTINCT (fld, col)
        INCLUDE (two, three)
        WITH (arg1=3, arg5='str')
        USING INDEX TABLESPACE tblspc,
    ADD CONSTRAINT pk PRIMARY KEY (fld, col)
        INCLUDE (four)
        WITH (ff=auto, gg=stuff)
        USING INDEX TABLESPACE tblspc;

-- Test SET/RESET actions on both table and column

ALTER TABLE foo SET (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC);
ALTER TABLE foo RESET (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC);
ALTER TABLE foo ALTER COLUMN baz
    SET (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC);
ALTER TABLE foo ALTER COLUMN baz
    RESET (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC);

-- Test out EXCLUDE constraints, as well as other more advanced index parameters on constraints

-- from https://www.postgresql.org/docs/15/rangetypes.html: basic usage (adapted for ALTER TABLE)
ALTER TABLE reservation ADD EXCLUDE USING gist (during WITH &&);
ALTER TABLE room_reservation ADD CONSTRAINT cons EXCLUDE USING gist (room WITH =, during WITH &&);

-- all the gnarly options: not every option is valid, but this will parse successfully on PG 15.
ALTER TABLE no_using ADD EXCLUDE (field WITH =) NOT DEFERRABLE INITIALLY IMMEDIATE NO INHERIT;
ALTER TABLE many_options ADD EXCLUDE
    USING gist (
        one WITH =,
        nulls_opclass nulls WITH =,
        nulls_last NULLS LAST WITH =,
        two COLLATE "en-US" opclass
            (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC)
            ASC NULLS FIRST WITH =,
        (two + 5) WITH =,
        myfunc(a, b) WITH =,
        myfunc_opclass(a, b) fop (opt=1, foo=2) WITH =,
        only_opclass opclass WITH =,
        desc_order DESC WITH =
    ) INCLUDE (a, b) WITH (idx_num = 5, idx_str = 'idx_value', idx_kw=DESC)
        USING INDEX TABLESPACE tblspc
        WHERE (field != 'def')
        DEFERRABLE NOT VALID INITIALLY DEFERRED;
