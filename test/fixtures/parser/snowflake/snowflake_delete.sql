DELETE FROM x USING y, z;

DELETE FROM x WHERE 1=2;

delete from leased_bicycles 
    using returned_bicycles
    where leased_bicycles.bicycle_id = returned_bicycles.bicycle_id;

delete from leased_bicycles 
    using (select bicycle_id as bicycle_id from returned_bicycles) as returned
    where leased_bicycles.bicycle_id = returned.bicycle_id;


delete from leased_bicycles 
    using (select bicycle_id as bicycle_id from returned_bicycles where 1=2) as returned
    where leased_bicycles.bicycle_id = returned.bicycle_id;

