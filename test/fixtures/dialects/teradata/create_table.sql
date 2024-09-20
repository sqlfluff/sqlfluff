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
