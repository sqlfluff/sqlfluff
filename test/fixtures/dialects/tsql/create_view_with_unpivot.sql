CREATE VIEW UnpivotView
AS
	-- Unpivot the table.
	SELECT VendorID, Employee, Orders
	FROM
	   (SELECT VendorID, Emp1, Emp2, Emp3, Emp4, Emp5
	   FROM pvt) p
	UNPIVOT
	   (Orders FOR Employee IN
		  (Emp1, Emp2, Emp3, Emp4, Emp5)
	) AS unpvt;
