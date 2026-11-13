SELECT q'[it's]', Q'{it's}', q'(it's)', q'<it's>' FROM dual;
SELECT q'!it's!', q'#it's#', q']it's]', q''it's'' FROM dual;
SELECT nq'[national text]', NQ'!national text!' FROM dual;
SELECT q'[a ] bracket and ''two quotes'']', q'[]' FROM dual;
SELECT q'[first line
second line]' FROM dual;
SELECT q'界it's界' FROM dual;
