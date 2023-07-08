CREATE LUA SCALAR SCRIPT my_average
    (a DOUBLE, b DOUBLE ORDER BY 1 desc)
RETURNS DOUBLE AS
    function run(ctx)
        if ctx.a == nil or ctx.b==nil
            then return NULL
        end
        return (ctx.a+ctx.b)/2
    end
/
CREATE LUA SCALAR SCRIPT my_average
    (a DOUBLE, b DOUBLE ORDER BY 1 desc)
RETURNS DOUBLE AS
    function run(ctx)
        if ctx.a == nil or ctx.b==nil
            then return NULL
        end
        x = 10
            /
            2
        return (ctx.a+ctx.b)
                    / 2
    end
/
