CREATE INDEX li1 ON entries_data(id, LENGTH(chunk));

CREATE INDEX acctchng_magnitude ON account_change(acct_no, abs(amt));

CREATE INDEX t2xy ON t2(x+y);
