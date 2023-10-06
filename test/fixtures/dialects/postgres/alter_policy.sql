ALTER POLICY account_managers ON accounts
    RENAME TO account_users;

ALTER POLICY account_managers ON accounts
    TO current_user;

ALTER POLICY account_managers ON accounts
    TO public, session_user;

ALTER POLICY account_managers ON accounts
    WITH CHECK (
        NOT accounts_is_excluded_full_name(full_name)
    );

ALTER POLICY account_managers ON accounts
    WITH CHECK (
        col > 10
    );

ALTER POLICY account_managers ON accounts
    USING (username = current_user);

ALTER POLICY sales_rep_is_self ON invoices
  WITH CHECK (sales_rep = CURRENT_USER AND CURRENT_USER IN (
    SELECT user_id FROM allowed_users
  ));
