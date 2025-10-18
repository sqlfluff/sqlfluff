SELECT onetable.f1, twotable.f1 FROM onetable FORCE INDEX (idx_index) inner join twotable on onetable.f1 = twotable.f1;
