alter pipe mypipe refresh prefix = 'd1/';
alter pipe mypipe refresh prefix = 'd1/' modified_after = '2018-07-30T13:56:46-07:00';
alter pipe if exists mypipe refresh;
alter pipe mypipe set comment = 'Pipe for North American sales data';
alter pipe mypipe set pipe_execution_paused = true comment = 'Pipe for North American sales data';
alter pipe mypipe set tag tag1 = 'value1', tag2 = 'value2';
alter pipe mypipe unset pipe_execution_paused;
alter pipe mypipe unset comment;
alter pipe mypipe unset tag foo, bar;
