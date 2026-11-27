ALTER TABLE ledger ENABLE RULE audit_rule;
ALTER TABLE ledger DISABLE RULE audit_rule;
ALTER TABLE ledger ENABLE REPLICA RULE audit_rule;
ALTER TABLE ledger ENABLE ALWAYS RULE audit_rule;
