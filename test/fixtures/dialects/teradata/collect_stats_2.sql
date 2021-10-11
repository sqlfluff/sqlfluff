collect statistics 
 column (Org_Unit_Code, Org_Unit_Type, Entity_Code) as Org_Descendant_NUPI, 
 column (Org_Unit_Type), 
 column (Entity_Code), 
 column (Org_Unit_Code, Entity_Code), 
 column (Entity_Code, Parent_Org_Unit_Code, Parent_Org_Unit_Type), 
 column (Org_Unit_Code), 
 column (Parent_Org_Unit_Code, Parent_Org_Unit_Type, Parent_Entity_Code) 
on sandbox_db.Org_Descendant;

