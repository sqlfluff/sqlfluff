"""Extract children and instruction metadata from a generated Rust parser source.

This module is a small utility script intended to be run from the root of the
sqlfluff repository (or a checked-out copy of the sqlfluffrs crate). It locates
a generated parser implementation file (parser.rs), parses out the CHILD_IDS
static array and nearby instruction comments, and prints a small slice of the
child id array together with human-readable comments for each child gid.
It also looks up a specific grammar instruction (by gid) to report its
first_child_idx and child_count fields.
"""

import re
from pathlib import Path

p = Path("sqlfluffrs/sqlfluffrs_dialects/src/dialect/ansi/parser.rs")
candidates = [
    Path("sqlfluffrs/sqlfluffrs_dialects/src/dialect/ansi/parser.rs"),
    Path("sqlfluffrs_dialects/src/dialect/ansi/parser.rs"),
    Path("sqlfluffrs/sqlfluffrs_dialects/src/dialect/ansi/parser.rs").resolve(),
]
p = None
for cand in candidates:
    if cand.exists():
        p = cand
        break
if p is None:
    raise SystemExit(f"Could not find generated parser.rs in any of: {candidates}")
s = p.read_text("utf-8")

# Build instruction comment map: look for lines like "// [123] Ref(Name)"
inst_comments = {}
for m in re.finditer(r"// \[(\d+)\] (.*)\n\s*GrammarInst", s):
    idx = int(m.group(1))
    inst_comments[idx] = m.group(2).strip()

# Find CHILD_IDS array
m = re.search(r"pub static CHILD_IDS: &\[u32\] = &\[([\s\S]*?)\];", s)
if not m:
    print("CHILD_IDS not found")
    exit(1)
arr_text = m.group(1)
# Remove comments and whitespace
arr_text = re.sub(r"//.*", "", arr_text)
arr_text = arr_text.replace("\n", " ")
arr_items = [it.strip() for it in arr_text.split(",") if it.strip()]
child_ids = [int(it) for it in arr_items]

offset = 1629
count = 5
slice_ids = child_ids[offset : offset + count]
print(f"CHILD_IDS[{offset}:{offset + count}] = {slice_ids}")
for i, gid in enumerate(slice_ids):
    comment = inst_comments.get(gid, "<no comment>")
    print(f"  child[{i}] = gid {gid}: {comment}")

# Also print the instruction for 2524 (the Sequence) to show child_count
seq_gid = 2524
m2 = re.search(rf"// \[{seq_gid}\][\s\S]*?GrammarInst \{{([\s\S]*?)\}}", s)
if m2:
    inst_body = m2.group(1)
    # find first_child_idx and child_count
    m3 = re.search(r"first_child_idx: (\d+),\s*\n\s*child_count: (\d+),", inst_body)
    if m3:
        print(
            f"Instruction {seq_gid} has first_child_idx={m3.group(1)} "
            f"child_count={m3.group(2)}"
        )
    else:
        print(f"Could not parse instruction body for {seq_gid}")
else:
    print(f"Instruction {seq_gid} not found")
