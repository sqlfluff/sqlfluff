-- A DLT materialized view may declare no columns at all, listing only
-- expectations and letting the column types come from the query.
CREATE OR REFRESH MATERIALIZED VIEW jhu_covid19_cleansed(
    CONSTRAINT valid_confirmed EXPECT (confirmed IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "The cleansed Johns Hopkins COVID-19 dataset."
TBLPROPERTIES ("quality" = "silver")
AS SELECT confirmed FROM live.jhu_covid19_raw;

-- Several expectations, with and without an ON VIOLATION action.
CREATE OR REFRESH MATERIALIZED VIEW loans_cleansed(
    CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE,
    CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_term EXPECT (term IS NOT NULL)
)
AS SELECT id, amount, term FROM live.loans_raw;

-- Expectations only, followed by a table constraint.
CREATE MATERIALIZED VIEW expectations_then_table_constraint(
    CONSTRAINT valid_id EXPECT (id IS NOT NULL),
    CONSTRAINT pk_id PRIMARY KEY (id)
)
AS SELECT id FROM live.source;

-- The documented order -- columns, then expectations, then table
-- constraints -- still parses.
CREATE MATERIALIZED VIEW columns_then_expectations(
    id BIGINT COMMENT "Primary identifier",
    amount DECIMAL(10, 2),
    CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT pk_id PRIMARY KEY (id)
)
AS SELECT id, amount FROM live.source;

-- Columns only, and no column list at all, both unchanged.
CREATE MATERIALIZED VIEW columns_only(
    id BIGINT,
    name STRING
)
AS SELECT id, name FROM live.source;

CREATE OR REFRESH MATERIALIZED VIEW no_column_list
AS SELECT 1 AS id;
