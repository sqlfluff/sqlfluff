CREATE INDEX li1 ON entries_data(id, LENGTH(chunk));

CREATE INDEX acctchng_magnitude ON account_change(acct_no, abs(amt));

CREATE INDEX t2xy ON t2(x+y);

CREATE UNIQUE INDEX team_leader ON person(team_id) WHERE is_team_leader;

CREATE INDEX ex1 ON tab1(a,b) WHERE a=5 OR b=6;

CREATE INDEX po_parent ON purchaseorder(parent_po) WHERE parent_po IS NOT NULL;

CREATE INDEX ex2 ON tab2(b,c) WHERE c IS NOT NULL;
