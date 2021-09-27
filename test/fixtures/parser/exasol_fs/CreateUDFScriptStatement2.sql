CREATE LUA SCALAR SCRIPT map_words(w varchar(10000))
EMITS (words varchar(100)) AS
function run(ctx)
    local word = ctx.w
    if (word ~= null)
    then
        for i in unicode.utf8.gmatch(word,'([%w%p]+)')
        do
            ctx.emit(i)
        end
    end
end
/
