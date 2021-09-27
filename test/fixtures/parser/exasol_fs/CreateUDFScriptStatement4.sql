CREATE OR REPLACE PYTHON SCALAR SCRIPT TEST.MYHELLOWORLD() RETURNS VARCHAR(2000) AS
l = exa.import_script('LIB.MYLIB')
def run(ctx):
    return l.helloWorld()
/
