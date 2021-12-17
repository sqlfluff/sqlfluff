merge
   schema1.table1 dst
using
   schema1.table1 src
on
   src.rn = 1
   and dst.e_date_to is null
   and dst.cc_id = src.cc_id
when matched
   then update
      set
         dst.l_id = src.l_id,
         dst.e_date_to = src.e_date_from
go

with source_data as
(
    select
        cc_id
        , cc_name
        , cc_description
    from
        DW.sch1.tbl1
    where
        e_date_to is null
        and l_id >= dd
        and l_id <= dd
)
merge
    DM.sch1.tbl2 dst
using
    source_data src
on
    src.cc_id = dst.cc_id
when
    matched
        then
            update
                set
                    dst.cc_name = src.cc_name
                    , dst.cc_description = src.cc_description
when
    not matched
        then
            insert
            (
                cc_id
                , cc_name
                , cc_description
            )
            values
            (
                cc_id
                , cc_name
                , cc_description
            );
go

merge
    DW.tt.dd dst
using
    LA.tt.dd src
    on dst.s_id = src.s_id
    and dst.c_id = src.c_id
when matched
    then update
        set
            dst.c_name = src.c_name
            , dst.col1 = src.col1
            , dst.col2 = src.col2
when not matched by target and src.c_id is not null
    then insert
        (
            s_id
            , c_id
            , c_name
            , col1
            , col2
        )
    values
        (
            src.s_id
            , src.c_id
            , src.c_name
            , src.col1
            , src.col2
        )
when not matched by source and s_id =1 in
                            ( select s_id from LA.g.tbl3)
    then update
        set
            dst.col1 = 'N'
            , dst.col2 = col2
;

go

MERGE Production.UnitMeasure AS tgt
    USING (SELECT @UnitMeasureCode, @Name) as src (UnitMeasureCode, Name)
    ON (tgt.UnitMeasureCode = src.UnitMeasureCode)
    WHEN MATCHED THEN
        UPDATE SET Name = src.Name
    WHEN NOT MATCHED THEN
        INSERT (UnitMeasureCode, Name)
        VALUES (src.UnitMeasureCode, src.Name)
    OUTPUT deleted.*, $action, inserted.* INTO #MyTempTable;
GO

MERGE Production.ProductInventory AS tgt
USING (SELECT ProductID, SUM(OrderQty) FROM Sales.SalesOrderDetail AS sod
    JOIN Sales.SalesOrderHeader AS soh
    ON sod.SalesOrderID = soh.SalesOrderID
    AND soh.OrderDate = @OrderDate
    GROUP BY ProductID) as src (ProductID, OrderQty)
ON (tgt.ProductID = src.ProductID)
WHEN MATCHED AND tgt.Quantity - src.OrderQty <= 0
    THEN DELETE
WHEN MATCHED
    THEN UPDATE SET tgt.Quantity = tgt.Quantity - src.OrderQty,
                    tgt.ModifiedDate = GETDATE()
OUTPUT $action, Inserted.ProductID, Inserted.Quantity,
    Inserted.ModifiedDate, Deleted.ProductID,
    Deleted.Quantity, Deleted.ModifiedDate;
GO

MERGE Production.ProductInventory AS pi
     USING (SELECT ProductID, SUM(OrderQty)
            FROM Sales.SalesOrderDetail AS sod
            JOIN Sales.SalesOrderHeader AS soh
            ON sod.SalesOrderID = soh.SalesOrderID
            AND soh.OrderDate BETWEEN '20030701' AND '20030731'
            GROUP BY ProductID) AS src (ProductID, OrderQty)
     ON pi.ProductID = src.ProductID
    WHEN MATCHED AND pi.Quantity - src.OrderQty >= 0
        THEN UPDATE SET pi.Quantity = pi.Quantity - src.OrderQty
    WHEN MATCHED AND pi.Quantity - src.OrderQty <= 0
        THEN DELETE
    OUTPUT $action, Inserted.ProductID, Inserted.LocationID,
        Inserted.Quantity AS NewQty, Deleted.Quantity AS PreviousQty;



