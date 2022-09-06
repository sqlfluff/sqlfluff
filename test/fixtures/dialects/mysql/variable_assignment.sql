SELECT @var1:=COUNT(*) FROM t1;

SET @var1:=0;

SET @var1:=@var2:=0;

UPDATE t1 SET c1 = 2 WHERE c1 = @var1:= 1;
