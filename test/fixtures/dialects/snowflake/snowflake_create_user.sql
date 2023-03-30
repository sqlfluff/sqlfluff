create user user1
    password='abc123'
    default_role = myrole
    display_name = user1
    login_name = my_login_name
    first_name = User1
    middle_name = abc
    last_name = Test1
    default_warehouse = my_default_warehouse
    default_namespace = my_default_namespace
    default_secondary_roles = ('ALL')
    must_change_password = true;

create user user2
    password='abc123'
    default_role = 'myrole'
    display_name = 'user 2'
    login_name = 'test login name'
    first_name = 'User'
    middle_name = 'abc'
    last_name = 'test2'
    default_warehouse = 'my_default_warehouse'
    default_namespace = 'my_default_namespace'
    must_change_password = false;
