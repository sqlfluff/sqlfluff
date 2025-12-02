DETACH RLS POLICY policy_concerts ON tickit_category_redshift FROM ROLE analyst, ROLE dbadmin;

DETACH RLS POLICY policy_concerts ON TABLE tickit_category_redshift FROM ROLE role1, user1;
