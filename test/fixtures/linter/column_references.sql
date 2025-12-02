select a, b.c, d.g, f as f1, f1 + 1 as f2
from z as a JOIN d using(f) where f2 > 1
-- NB: `f` appears in the USING clause and so shouldn't fail on RF02
