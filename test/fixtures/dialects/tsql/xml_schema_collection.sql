-- CREATE
CREATE XML SCHEMA COLLECTION dbo.SomeXmlSchemaCollection
    AS N'<?xml version="1.0" encoding="UTF-16"?>
<xsd:schema targetNamespace="https://schemas.microsoft.com/sqlserver/2004/07/adventure-works/ProductModelManuInstructions"
   xmlns          ="https://schemas.microsoft.com/sqlserver/2004/07/adventure-works/ProductModelManuInstructions"
   elementFormDefault="qualified"
   attributeFormDefault="unqualified"
   xmlns:xsd="http://www.w3.org/2001/XMLSchema" >

    <xsd:complexType name="StepType" mixed="true" >
        <xsd:choice  minOccurs="0" maxOccurs="unbounded" >
            <xsd:element name="tool" type="xsd:string" />
            <xsd:element name="material" type="xsd:string" />
            <xsd:element name="blueprint" type="xsd:string" />
            <xsd:element name="specs" type="xsd:string" />
            <xsd:element name="diag" type="xsd:string" />
        </xsd:choice>
    </xsd:complexType>

    <xsd:element  name="root">
        <xsd:complexType mixed="true">
            <xsd:sequence>
                <xsd:element name="Location" minOccurs="1" maxOccurs="unbounded">
                    <xsd:complexType mixed="true">
                        <xsd:sequence>
                            <xsd:element name="step" type="StepType" minOccurs="1" maxOccurs="unbounded" />
                        </xsd:sequence>
                        <xsd:attribute name="LocationID" type="xsd:integer" use="required"/>
                        <xsd:attribute name="SetupHours" type="xsd:decimal" use="optional"/>
                        <xsd:attribute name="MachineHours" type="xsd:decimal" use="optional"/>
                        <xsd:attribute name="LaborHours" type="xsd:decimal" use="optional"/>
                        <xsd:attribute name="LotSize" type="xsd:decimal" use="optional"/>
                    </xsd:complexType>
                </xsd:element>
            </xsd:sequence>
        </xsd:complexType>
    </xsd:element>
</xsd:schema>';

DECLARE @MySchemaCollection AS NVARCHAR (MAX) = '';
CREATE XML SCHEMA COLLECTION AnotherXmlSchemaCollection
    AS @MySchemaCollection;
GO

-- ALTER
ALTER XML SCHEMA COLLECTION MyColl ADD '
  <schema xmlns="http://www.w3.org/2001/XMLSchema"
         targetNamespace="https://MySchema/test_xml_schema">
     <element name="anotherElement" type="byte"/>
 </schema>';
 DECLARE @NewItem AS NVARCHAR (MAX) = '
  <schema xmlns="http://www.w3.org/2001/XMLSchema"
         targetNamespace="https://MySchema/test_xml_schema">
     <element name="yetAnotherElement" type="byte"/>
 </schema>';
 ALTER XML SCHEMA COLLECTION dbo.MyColl ADD @NewItem;

-- DROP
DROP XML SCHEMA COLLECTION dbo.SomeXmlSchemaCollection;
DROP XML SCHEMA COLLECTION AnotherXmlSchemaCollection;
GO
