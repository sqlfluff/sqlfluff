DELETE FROM MY_TABLE
WHERE 1=1
;

DELETE FROM MY_TABLE
WHERE MY_COL > 10
;

DELETE FROM MY_TABLE
WHERE ID IN (SELECT ID FROM ANOTHER_TABLE)
AND ID <> 5
;

DEL FROM MY_TABLE
WHERE 1=1
;

DEL FROM MY_TABLE
WHERE MY_COL > 10
;

DEL FROM MY_TABLE
WHERE ID IN (SELECT ID FROM ANOTHER_TABLE)
AND ID <> 5
;
