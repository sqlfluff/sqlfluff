SELECT onetable.f1, twotable.f1 FROM onetable left join twotable FORCE INDEX (idx_index) on onetable.f1 = twotable.f1;
