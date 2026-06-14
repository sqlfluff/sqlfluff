select e1.abc
from exp1 e1, exp2 e2
where
    e1.key (+) = e2.key
    and e1.str (+) = 'smth';
