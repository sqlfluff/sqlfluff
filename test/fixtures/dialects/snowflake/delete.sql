delete from leased_bicycles;

delete from leased_bicycles as lb;

delete from x using y, z;

delete from x where 1 = 2;

delete from leased_bicycles
    using returned_bicycles
    where leased_bicycles.bicycle_id = returned_bicycles.bicycle_id;

delete from leased_bicycles as lb
    using returned_bicycles as rb
    where lb.bicycle_id = rb.bicycle_id;

delete from leased_bicycles lb
    using returned_bicycles rb
    where lb.bicycle_id = rb.bicycle_id;

delete from leased_bicycles
    using returned_bicycles, broken_bicycles
    where leased_bicycles.bicycle_id = returned_bicycles.bicycle_id
        and leased_bicycles.bicycle_id = broken_bicycles.bicycle_id;

delete from leased_bicycles as lb
    using returned_bicycles as rb, broken_bicycles as bb
    where lb.bicycle_id = rb.bicycle_id
        and lb.bicycle_id = bb.bicycle_id;

delete from leased_bicycles lb
    using returned_bicycles rb, broken_bicycles bb
    where lb.bicycle_id = rb.bicycle_id
        and lb.bicycle_id = bb.bicycle_id;

delete from leased_bicycles
    using (select bicycle_id as bicycle_id from returned_bicycles) as returned
    where leased_bicycles.bicycle_id = returned.bicycle_id;


delete from leased_bicycles
    using (select bicycle_id as bicycle_id from returned_bicycles where 1=2) as returned
    where leased_bicycles.bicycle_id = returned.bicycle_id;
