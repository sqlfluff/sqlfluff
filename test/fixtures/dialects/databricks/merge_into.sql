merge into mydb_stg.dummy_table as dest
using
_tempDeDupRaw as src
on
dest.col_a = src.col_a
and dest.col_b = src.col_b
and dest.col_c = src.col_c
and dest.col_d <=> src.col_d
and dest.col_e <=> src.col_e
and dest.col_f <=> src.col_f
and dest.col_g <=> src.col_g
when matched
and dest.ts_extracted < src.ts_extracted
and not (dest.id = src.id)
then
update
set
dest.file_path = src.file_path
, dest.ts_updated = current_timestamp()
, dest.ts_inserted_raw = src.ts_inserted_raw
, dest.ts_loaded_raw = src.ts_loaded_raw
, dest.ts_loaded_drp = src.ts_loaded_drp
, dest.ts_extracted = src.ts_extracted
, dest.id = src.id
when not matched by target
then
insert (
file_path
, ts_inserted_stg
, ts_updated
, ts_inserted_raw
, ts_loaded_raw
, ts_loaded_drp
, ts_extracted
, col_a
, col_b
, col_c
, col_d
, col_e
, col_f
, col_g
, id
) values (
src.file_path
, current_timestamp()
, current_timestamp()
, src.ts_inserted_raw
, src.ts_loaded_raw
, src.ts_loaded_drp
, src.ts_extracted
, src.col_a
, src.col_b
, src.col_c
, src.col_d
, src.col_e
, src.col_f
, src.col_g
, src.id
)
when not matched by source
then
delete
;

merge into mydb_stg.dummy_table as dest
using _tempDeDupRaw as src
on dest.id = src.id
when matched and src.is_update = true then
update set *
when not matched then
insert *
;

merge into mydb_stg.dummy_table as dest
using _tempDeDupRaw as src
on dest.id = src.id
when not matched by target and src.is_valid = true then
insert (id, file_path) values (src.id, src.file_path)
when not matched by source and dest.is_active = true then
update set dest.is_active = false
