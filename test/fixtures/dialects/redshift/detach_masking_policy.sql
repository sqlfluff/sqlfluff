DETACH MASKING POLICY mask_credit_card ON credit_cards (credit_card) FROM PUBLIC;

DETACH MASKING POLICY mask_credit_card ON credit_cards (credit_card) FROM ROLE analytics_role;

DETACH MASKING POLICY db1.mask_policy ON db1.sch1.table1 (col1, col2) FROM USER user1;
