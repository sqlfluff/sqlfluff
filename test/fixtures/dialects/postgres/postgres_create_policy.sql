CREATE POLICY account_managers ON accounts
    TO current_user;

CREATE POLICY account_managers ON sch.accounts
    AS permissive
    FOR ALL
    TO managers;

CREATE POLICY account_managers ON accounts
    TO public, session_user;

CREATE POLICY account_managers ON accounts
    WITH CHECK (
        NOT accounts_is_excluded_full_name(full_name)
    );

CREATE POLICY emp_rls_policy ON employee FOR all TO public USING (ename=current_setting('rls.ename'));

CREATE POLICY account_managers ON accounts
    WITH CHECK (
        col > 10
    );


CREATE POLICY account_managers ON accounts
    USING (username = current_user);
