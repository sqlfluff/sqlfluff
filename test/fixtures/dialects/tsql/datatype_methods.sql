-- Function Case mismatch
SELECT SomeSchema.XValue();
SELECT SomeSchema.Value();
SELECT SomeSchema.VALUE();
-- Method case case match
SELECT SomeColumn.value(), SomeColumn FROM dbo.SomeTable;

SELECT @XML.value('.', 'nvarchar(max)') Col1;
SELECT CONVERT(xml, N'<r></r>').value('.','nvarchar(max)');
SELECT (SELECT CONVERT(xml, N'<r></r>')).value('.','nvarchar(max)');

select @xml.query('.').query('.');

SELECT @hierarchyid.GetAncestor(2) parent_id;
SELECT convert(hierarchyid, '/1/1/2').GetAncestor(2) parent;
select @geometry.STEndPoint() EndPt;

SELECT convert(hierarchyid, '/1/1/2').GetAncestor(2).GetAncestor(2) parent;

SELECT @geography.STArea() area;
SELECT @geography.STDistance(@other_geography) dist;

SELECT na.Loc.query('.') FROM SomeTable CROSS APPLY SomeXMLColumn.nodex('/root/Location') AS na(Loc);
SELECT T.c.query('.') FROM @x.nodes('/Root/row') T(c);
GO
