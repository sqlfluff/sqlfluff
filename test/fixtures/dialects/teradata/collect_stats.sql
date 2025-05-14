COLLECT STATISTICS COLUMN ( IND_TIPO_TARJETA ) ON DB_1.TABLE_1;

COLLECT STATISTICS INDEX ( COD_TARJETA, COD_EST, IND_TIPO_TARJETA, FEC_ANIO_MES ) ON DB_1.TABLE_1;

COLLECT STATISTICS
COLUMN o_orderstatus
ON orders;

COLLECT STATISTICS
    USING SYSTEM THRESHOLD FOR CURRENT
    COLUMN (o_orderstatus, o_orderkey)
    ON orders;

COLLECT STATS COLUMN ( IND_TIPO_TARJETA ) ON DB_1.TABLE_1;

COLLECT STAT COLUMN ( IND_TIPO_TARJETA ) ON DB_1.TABLE_1;

COLLECT STATS COLUMN IND_TIPO_TARJETA ON DB_1.TABLE_1;

COLLECT STATS INDEX ( COD_TARJETA, COD_EST, IND_TIPO_TARJETA, FEC_ANIO_MES ) ON DB_1.TABLE_1;

collect statistics
 column (Org_Unit_Code, Org_Unit_Type, Entity_Code) as Org_Descendant_NUPI,
 column (Org_Unit_Type),
 column (Entity_Code),
 column (Org_Unit_Code, Entity_Code),
 column (Entity_Code, Parent_Org_Unit_Code, Parent_Org_Unit_Type),
 column (Org_Unit_Code),
 column (Parent_Org_Unit_Code, Parent_Org_Unit_Type, Parent_Entity_Code)
on sandbox_db.Org_Descendant;

COLLECT STATISTICS ON table_1 COLUMN (column_1, column_2);

COLLECT STATISTICS ON orders
COLUMN (quant_ord, PARTITION, quant_shpd);

COLLECT STATISTICS ON table_1 COLUMN PARTITION;
