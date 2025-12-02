DECLARE @MyTableVar TABLE(
    EmpID INT NOT NULL,
    OldVacationHours INT,
    NewVacationHours INT,
    ModifiedDate DATETIME,
    PRIMARY KEY (EmpID)
);

DECLARE
    @myTable TABLE
    (
        ID INT,
        MyCol1 BIT,
        MyCol2 BIT,
        MyComputedCol AS (
            CASE
                WHEN MyCol1 & MyCol2 = 0
                    THEN 1
                WHEN MyCol2 = 0 THEN 2
                ELSE 3
            END
        )
    );
