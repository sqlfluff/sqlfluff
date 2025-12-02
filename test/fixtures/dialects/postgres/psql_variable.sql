\prompt 'From Member #: ' m1
\prompt 'To Member #: ' m2
\prompt 'Charge Account #: ' a

SELECT
  'from' AS direction,
  users.email,
  rona_mms_charge_accounts.account_number
FROM memberships
JOIN users ON users.id = memberships.user_id
LEFT OUTER JOIN rona_mms_charge_accounts ON users.id = rona_mms_charge_accounts.customer_id
WHERE memberships.code = (:m1)::text
                          AND rona_mms_charge_accounts.account_number = lpad((:a)::text, 10, '0');

\prompt 'From Member #: ' m1
\prompt 'To Member #: ' m2
\prompt 'Charge Account #: ' a

SELECT
  'from' AS direction,
  users.email,
  rona_mms_charge_accounts.account_number
FROM memberships
JOIN users ON users.id = memberships.user_id
LEFT OUTER JOIN rona_mms_charge_accounts ON users.id = rona_mms_charge_accounts.customer_id
WHERE memberships.code = :'m1'
                          AND rona_mms_charge_accounts.account_number = lpad(:'a', 10, '0');
