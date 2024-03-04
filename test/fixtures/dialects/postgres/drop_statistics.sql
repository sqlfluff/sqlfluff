DROP STATISTICS IF EXISTS
    accounting.users_uid_creation,
    public.grants_user_role;

DROP STATISTICS foo CASCADE;
DROP STATISTICS bar RESTRICT;
