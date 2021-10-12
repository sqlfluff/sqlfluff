CREATE OR REPLACE JAVA SCALAR SCRIPT LIB.MYLIB() RETURNS VARCHAR(2000) AS
class MYLIB {
    static String helloWorld(){
            return "Hello Java World!";
    }
}
/
