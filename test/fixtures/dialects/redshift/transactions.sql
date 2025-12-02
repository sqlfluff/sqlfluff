begin;

start transaction;

begin work;

begin transaction isolation level serializable;

begin transaction isolation level serializable read only;

start transaction read write;

commit;

end work;

commit transaction;

rollback;

abort work;

rollback transaction;
