
delimiter ~
drop procedure if exists `zproc_workflow_status_complete`~
create procedure `zproc_workflow_status_complete`(
                                                `_in_workflow_id`       bigint(20)
                                              , `_in_status`            varchar(32)
                                              ,  out _out_err_msg       varchar(1024)
                                                 )
z_proc:begin
    if (select count(*) from xworkflow_rtq where id = _in_workflow_id) = 0 then
      set @errmsg =      concat('input workflow id not found (' , _in_workflow_id, '), ',       sysdate(6));
      leave z_block;
    end if;

end z_proc~
delimiter ;