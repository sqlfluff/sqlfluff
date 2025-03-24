create user user1
    type = person
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
    type = 'service'
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

create user user3
    type = person
    rsa_public_key = '<BASE 64 ENCODED PUBLIC KEY>'
    default_role = myrole
    display_name = user1
    login_name = my_login_name
    first_name = User1
    middle_name = abc
    last_name = Test1
    default_warehouse = my_default_warehouse
    default_namespace = my_default_namespace
    default_secondary_roles = ('ALL');

create user user4
    type = person
    rsa_public_key = '<BASE 64 ENCODED PUBLIC KEY>'
    rsa_public_key_2 = '<SECOND BASE 64 ENCODED PUBLIC KEY>'
    default_role = myrole
    display_name = user1
    login_name = my_login_name
    first_name = User1
    middle_name = abc
    last_name = Test1
    default_warehouse = my_default_warehouse
    default_namespace = my_default_namespace
    default_secondary_roles = ('ALL');
