create table sandbox_db.Org_Descendant
(
 Org_Unit_Code char(6) character set unicode not null,
 Org_Unit_Type char(3) character set unicode not null,
 Entity_Code varchar(10) uppercase not null,
 Parent_Org_Unit_Code char(6) character set unicode not null,
 Parent_Org_Unit_Type char(3) character set unicode not null,
 Parent_Entity_Code varchar(10) uppercase not null
)
primary index Org_Descendant_NUPI (Org_Unit_Code, Org_Unit_Type, Entity_Code)
;

collect statistics
 column (Org_Unit_Code, Org_Unit_Type, Entity_Code) as Org_Descendant_NUPI,
 column (Org_Unit_Type),
 column (Entity_Code),
 column (Org_Unit_Code, Entity_Code),
 column (Entity_Code, Parent_Org_Unit_Code, Parent_Org_Unit_Type),
 column (Org_Unit_Code),
 column (Parent_Org_Unit_Code, Parent_Org_Unit_Type, Parent_Entity_Code)
on sandbox_db.Org_Descendant;

comment on table sandbox_db.Org_Descendant is 'View with all Org_Unit_Ids on all levels';
comment on column sandbox_db.Org_Descendant.Org_Unit_Code is 'Organisational unit code';
comment on column sandbox_db.Org_Descendant.Org_Unit_Type is 'The type of organization such as branch, region, team, call center';
comment on column sandbox_db.Org_Descendant.Entity_Code is 'Owning entity code';
comment on column sandbox_db.Org_Descendant.Parent_Org_Unit_Code is 'Organisational unit code';
comment on column sandbox_db.Org_Descendant.Parent_Org_Unit_Type is 'The type of organization such as branch, region, team, call center';
comment on column sandbox_db.Org_Descendant.Parent_Entity_Code is 'Owning entity code parent';

CREATE VOLATILE MULTISET TABLE date_control (calculation_date DATE FORMAT 'yyyy-mm-dd' ) PRIMARY INDEX (calculation_date);
CREATE MULTISET VOLATILE TABLE date_control (calculation_date DATE FORMAT 'yyyy-mm-dd' ) PRIMARY INDEX (calculation_date);

-- Testing of the specific create table begin options
CREATE MULTISET TABLE CONSUMOS, NO FALLBACK, NO BEFORE JOURNAL, NO AFTER JOURNAL,
     CHECKSUM = DEFAULT, DEFAULT MERGEBLOCKRATIO
(
    FIELD1 CHAR(9)
)
PRIMARY INDEX( FIELD1 );

-- Testing of the specific column options
CREATE MULTISET TABLE TABLE_2
(
    CHAR_FIELD CHAR(19) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
    DATE_FIELD DATE FORMAT 'YYYY-MM-DD' NOT NULL,
    BYTE_FIELD BYTEINT COMPRESS 0,
    DECIMAL_FIELD DECIMAL(15, 2) COMPRESS (50.00, 45.50, 40.00, 30.00, 27.80, 27.05, 20.00, 17.87, 17.56, 17.41, 17.26, 17.11, 16.96, 16.82, 16.68),
    TIMESTAMP_FIELD TIMESTAMP(6) NOT NULL
)
PRIMARY INDEX( CHAR_FIELD, DATE_FIELD, BYTE_FIELD );

-- Testing of the specific create table end options
CREATE MULTISET TABLE NUM_LTR_DESVINCULADOS_ADH
(
    DES_EVENTO VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC COMPRESS ('Cambio de bandera', 'Cierre'),
    IND_CONTINUA BYTEINT COMPRESS
 )
PRIMARY INDEX( COD_TARJETA, COD_EST, FEC_CIERRE_EST, IND_TIPO_TARJETA )
PARTITION BY RANGE_N (FEC_OPERACION BETWEEN DATE '2007-01-01' AND DATE '2022-01-01' EACH INTERVAL '1' MONTH, NO RANGE OR UNKNOWN)
INDEX HOPR_TRN_TRAV_SIN_MP_I ( IND_TIPO_TARJETA );

create table sandbox_db.Org_Descendant
(
 Org_Unit_Code char(6) character set unicode not null,
 Org_Unit_Type char(3) character set unicode not null,
 Entity_Code varchar(10) uppercase not null,
 Parent_Org_Unit_Code char(6) character set unicode not null,
 Parent_Org_Unit_Type char(3) character set unicode not null,
 Parent_Entity_Code varchar(10) uppercase not null
)
primary index Org_Descendant_NUPI (Org_Unit_Code, Org_Unit_Type, Entity_Code)
;

CREATE VOLATILE TABLE a AS (SELECT 'A' AS B) WITH DATA ON COMMIT PRESERVE ROWS;

CREATE VOLATILE TABLE b AS (SELECT 'A' AS B) WITH DATA ON COMMIT DELETE ROWS;

CREATE VOLATILE TABLE c AS (SELECT 'A' AS B) WITH NO DATA;

CREATE VOLATILE TABLE e AS (SELECT 'A' AS B) WITH NO DATA AND STATS;

CREATE VOLATILE TABLE f AS (SELECT 'A' AS B) WITH NO DATA AND NO STATS;

CREATE VOLATILE TABLE g AS (SELECT 'A' AS B) WITH NO DATA AND STATISTICS;

CREATE VOLATILE TABLE h AS (SELECT 'A' AS B) WITH NO DATA AND NO STATISTICS ON COMMIT PRESERVE ROWS;

-- Testing of the set tables with options
CREATE SET TABLE TABLE_2, FALLBACK ,
    NO BEFORE JOURNAL,
    NO AFTER JOURNAL,
    CHECKSUM = DEFAULT,
    DEFAULT MERGEBLOCKRATIO,
    MAP = TD_MAP1 (
    CHAR_FIELD CHAR(19) CHARACTER
    SET
    LATIN NOT CASESPECIFIC NOT NULL,
    DATE_FIELD DATE FORMAT 'YYYY-MM-DD' NOT NULL,
    BYTE_FIELD BYTEINT COMPRESS 0,
    DECIMAL_FIELD DECIMAL(15, 2) COMPRESS (
        50.00,
        45.50,
        40.00,
        30.00,
        27.80,
        27.05,
        20.00,
        17.87,
        17.56,
        17.41,
        17.26,
        17.11,
        16.96,
        16.82,
        16.68
    ),
    TIMESTAMP_FIELD TIMESTAMP(6) NOT NULL
) PRIMARY INDEX (CHAR_FIELD, DATE_FIELD, BYTE_FIELD);
