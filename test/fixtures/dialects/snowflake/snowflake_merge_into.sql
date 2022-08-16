ALTER TABLE xxxx.example_table MODIFY COLUMN employeeCode SET MASKING POLICY example_MASKING_POLICY;

merge into target_table using source_table
    on target_table.id = source_table.id
    when matched then
        update set target_table.description = source_table.description;

merge into t1 using t2 on t1.t1key = t2.t2key
    when matched and t2.marked = 1 then delete;

merge into t1 using t2 on t1.t1key = t2.t2key
    when not matched and t2.marked = 1 then insert (marked) values (1);
