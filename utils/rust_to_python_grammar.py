#!/usr/bin/env python3
"""Convert generated Rust grammar file back into Python grammar.

Usage:
  python3 utils/rust_to_python_grammar.py \
      --in sqlfluffrs_dialects/src/dialect/ansi/parser.rs \
      --out agent_output/rust_grammar_ansi.json

The script extracts the `INSTRUCTIONS` table, the `CHILD_IDS` array and the
`STRINGS` table and emits a JSON file with one entry per grammar id. Each
entry contains the variant, numeric fields and resolved child id list.

This is intentionally lightweight and dependency-free so it can be run
without installing extra packages.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Any, Dict, List


def extract_block(text: str, start_marker: str) -> str:
    """Extract a block of text.

    Extracts from the input string starting at the given marker and ending at the
    next occurrence of '];'. Raises RuntimeError if the markers are not found.
    """
    i = text.find(start_marker)
    if i == -1:
        raise RuntimeError(f"start marker not found: {start_marker}")
    j = text.find("];", i)
    if j == -1:
        raise RuntimeError("end of block not found")
    return text[i : j + 2]


def parse_instructions(block: str) -> List[Dict[str, Any]]:
    """Parse the INSTRUCTIONS block.

    Returns a list of instruction dictionaries. Extracts variant, child indices,
    counts, flags, parse mode, and comments.
    """
    lines = block.splitlines()
    insts = []
    last_comment = None
    for ln in lines:
        ln = ln.strip()
        m = re.match(r"// \[(\d+)\] (.*)", ln)
        if m:
            # capture comment for next GrammarInst
            last_comment = m.group(2).strip()
            continue
        if ln.startswith("GrammarInst") or "GrammarInst {" in ln:
            # Combine the line in case the struct is on multiple lines
            # We gather the full struct by joining until '},' is found
            # Start from current index to collect remainder lines
            # Simpler: extract useful fields with regex from ln and following text
            # We'll extract variant/first_child_idx/child_count/min_times
            #   /first_terminator_idx/terminator_count
            variant_m = re.search(r"variant:\s*GrammarVariant::(\w+)", ln)
            fc_m = re.search(r"first_child_idx:\s*(\d+)", ln)
            cc_m = re.search(r"child_count:\s*(\d+)", ln)
            mt_m = re.search(r"min_times:\s*(\d+)", ln)
            ft_m = re.search(r"first_terminator_idx:\s*(\d+)", ln)
            tc_m = re.search(r"terminator_count:\s*(\d+)", ln)
            flags_m = re.search(r"flags:\s*GrammarFlags::from_bits\((\d+)\)", ln)
            pm_m = re.search(r"parse_mode:\s*ParseMode::(\w+)", ln)
            inst = {
                "variant": variant_m.group(1) if variant_m else None,
                "first_child_idx": int(fc_m.group(1)) if fc_m else 0,
                "child_count": int(cc_m.group(1)) if cc_m else 0,
                "min_times": int(mt_m.group(1)) if mt_m else 0,
                "first_terminator_idx": int(ft_m.group(1)) if ft_m else 0,
                "terminator_count": int(tc_m.group(1)) if tc_m else 0,
                "flags": int(flags_m.group(1)) if flags_m else 0,
                "parse_mode": pm_m.group(1) if pm_m else None,
                "comment": last_comment,
            }
            last_comment = None
            insts.append(inst)
    return insts


def parse_number_array(block: str) -> List[int]:
    """Parse a Rust array of numbers."""
    # extract all integers
    nums = re.findall(r"\b(\d+)\b", block)
    return [int(x) for x in nums]


def parse_strings(block: str) -> List[str]:
    """Parse a Rust array of strings."""
    # find all double-quoted strings
    strs = re.findall(r'"((?:\\.|[^\\"])*)"', block)
    # unescape simple escapes
    return [s.encode("utf-8").decode("unicode_escape") for s in strs]


def main() -> None:
    """Main entry point.

    Parses arguments, reads the Rust grammar file, extracts tables, and writes
    the output JSON file with grammar instructions, child ids, and strings.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", required=True, help="path to parser.rs")
    p.add_argument("--out", dest="outfile", required=True, help="path to output JSON")
    args = p.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        text = f.read()

    inst_block = extract_block(text, "pub static INSTRUCTIONS: &[GrammarInst] = &[")
    insts = parse_instructions(inst_block)

    child_block = extract_block(text, "pub static CHILD_IDS: &[u32] = &[")
    child_ids = parse_number_array(child_block)

    # Terminators (optional) and STRINGS
    strings_block = extract_block(text, "pub static STRINGS: &[&str] = &[")
    strings = parse_strings(strings_block)

    # Attach children to each instruction
    for idx, inst in enumerate(insts):
        # Include the instruction index (grammar id) explicitly so callers
        # can reference the numeric id without relying on list position.
        inst["index"] = idx
        start = inst["first_child_idx"]
        count = inst["child_count"]
        if count:
            inst["children"] = child_ids[start : start + count]
        else:
            inst["children"] = []
        # Attempt to attach a human name from the comment when present
        if inst.get("comment"):
            inst["label"] = inst["comment"]

    out = {
        "instruction_count": len(insts),
        "child_ids_count": len(child_ids),
        "strings_count": len(strings),
        "strings": strings,
        "instructions": insts,
    }

    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(
        f"Wrote {args.outfile}: {len(insts)} instructions, "
        f"{len(child_ids)} child ids, {len(strings)} strings"
    )


if __name__ == "__main__":
    main()
