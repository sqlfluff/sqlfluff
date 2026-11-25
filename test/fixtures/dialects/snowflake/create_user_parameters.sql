create user example_user abort_detached_query = false;

create user example_user2
    default_role = my_role
    use_cached_result = false
    query_tag = 'my tag'
    statement_timeout_in_seconds = 3600
    network_policy = my_policy
    comment = 'with parameters';

create user example_user3 autocommit = true, binary_output_format = hex, timezone = 'UTC';
