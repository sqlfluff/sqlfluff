CREATE PYTHON SCALAR SCRIPT sample_simple (...) EMITS (...) AS
def run(ctx):
 ctx.emit(True, False)
/
