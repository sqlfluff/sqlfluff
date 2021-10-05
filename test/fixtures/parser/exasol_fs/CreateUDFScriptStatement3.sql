CREATE OR REPLACE PYTHON3 SCALAR SCRIPT LIB.MYLIB() RETURNS INT AS
def helloWorld():
    return "Hello Python3 World!"
/
