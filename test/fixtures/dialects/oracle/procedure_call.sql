-- Oracle PL/SQL procedure call without arguments and without brackets

begin
    my_procedure;
end;
/

begin
    schema.pkg.my_procedure;
end;
/

begin
    pkg.my_procedure;
    DBMS_OUTPUT.PUT_LINE('test');
end;
/
