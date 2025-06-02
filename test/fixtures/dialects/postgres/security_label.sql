SECURITY LABEL FOR selinux ON TABLE mytable IS 'system_u:object_r:sepgsql_table_t:s0';
SECURITY LABEL FOR selinux ON TABLE mytable IS NULL;
SECURITY LABEL ON FUNCTION show_credit(int) IS 'system_u:object_r:sepgsql_trusted_proc_exec_t:s0';
SECURITY LABEL ON COLUMN customer.credit IS 'system_u:object_r:sepgsql_secret_table_t:s0';
SECURITY LABEL FOR anon ON ROLE skynet IS 'MASKED';
SECURITY LABEL FOR anon ON COLUMN customer.first_name IS 'MASKED WITH FUNCTION anon.dummy_first_name()';
