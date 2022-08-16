declare var1 int64;
declare var2, var3 string;
declare var4 default 'value';
declare var5 int64 default 1 + 2;
declare var6 string(10);
declare var7 numeric(5, 2);
declare arr1 array<string>;
declare arr2 default ['one', 'two'];
declare arr3 default [];
declare arr4 array<string> default ['one', 'two'];
declare arr5 array<string(10)>;
declare str1 struct<f1 string, f2 string>;
declare str2 struct<f1 string, f2 string> default struct('one', 'two');
declare str3 default struct('one', 'two');
declare str4 struct<f1 string, f2 string> default ('one', 'two');
declare str5 struct<f1 string(10), f2 string(10)>;
-- Defining variables in quoted names
declare `var1` string;
declare `var1` string default 'value';
declare `var1`, `var1` string;
-- Defining variables mixing quoted and unquoted names
declare var1, `var2` string;
declare var1, `var2` string default 'value';
