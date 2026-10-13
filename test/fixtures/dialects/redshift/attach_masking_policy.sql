ATTACH MASKING POLICY mask_credit_card ON credit_cards (credit_card) TO PUBLIC;

ATTACH MASKING POLICY mask_credit_card ON credit_cards (credit_card) USING (credit_card) TO ROLE analytics_role PRIORITY 10;

ATTACH MASKING POLICY db1.mask_policy ON db1.sch1.table1 (col1, col2) USING (col1, col2) TO USER user1;
