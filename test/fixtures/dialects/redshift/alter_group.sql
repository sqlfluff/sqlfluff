alter group admin_group
add user dwuser;
alter group admin_group
add user dwuser1, dwuser2;

alter group admin_group
drop user dwuser;
alter group admin_group
drop user dwuser1, dwuser2;

alter group admin_group
rename to administrators;

alter group admin_group
add user "test.user";

alter group "admin_group"
add user "test.user";
