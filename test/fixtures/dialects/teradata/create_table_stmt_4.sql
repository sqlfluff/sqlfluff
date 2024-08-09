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
