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

ALTER TABLE distributors RENAME COLUMN address TO city;

ALTER TABLE distributors RENAME TO suppliers;

ALTER TABLE distributors RENAME CONSTRAINT zipchk TO zip_check;

ALTER TABLE distributors ALTER COLUMN street SET NOT NULL;

ALTER TABLE distributors ALTER COLUMN street DROP NOT NULL;

ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);

ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5) NO INHERIT;

ALTER TABLE distributors DROP CONSTRAINT zipchk;

ALTER TABLE ONLY distributors DROP CONSTRAINT zipchk;

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address);

ALTER TABLE distributors ADD CONSTRAINT distfk FOREIGN KEY (address) REFERENCES addresses (address) NOT VALID;

ALTER TABLE distributors VALIDATE CONSTRAINT distfk;

ALTER TABLE distributors ADD CONSTRAINT dist_id_zipcode_key UNIQUE (dist_id, zipcode);

ALTER TABLE distributors ADD PRIMARY KEY (dist_id);

ALTER TABLE distributors SET TABLESPACE fasttablespace;

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

ALTER TABLE landing.workorderhistory
ADD CONSTRAINT workorder_id_foreign_key
FOREIGN KEY(workorderid) REFERENCES landing.workorder(id);

ALTER TABLE my_table ADD COLUMN IF NOT EXISTS foo TEXT;

ALTER TABLE public.obm_buildings
OWNER to postgres;
