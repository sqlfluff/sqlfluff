# Reflow Primer

Several SQLFluff rules are concerned with layout and the placement
of segments with respect to whitespace and newlines. This is reflow.

The benefit of centralising reflow routines is that interdependencies
can be resolved and duplicate code can be reduced.

The challenge of centralising reflow routines is that separating out
the functionality to allow rules to _selectively_ apply element of
that logic without defaulting to a full reflow.

In the interests of separating this out, there are a few distinct
elements of reflow logic:
1. _Indentation_. This is the most obvious one we think of. This
   is concerned _only with the amount of leading whitespace at the_
   _start of lines_.
2. _Line Length_. This is concerned only with the total amount of
   characters on a line (including the amount of leading whitespace).
3. _Spacing_. This is concerned only with the amount of whitespace
   between elements on a line. **NB:** trailing whitespace is in
   this understanding, a special case of _Spacing_.
4. _Line Breaks_. This is concerned only with where line breaks are
   introduced within sequences of segments (usually, but not
   exclusively without reference to changes in indentation). This
   would (as an example) include the enforcement of trailing or
   leading commas.

It follows that each of these elements has dependencies on each other:
1. _Spacing_ will influence the _Line Length_.
2. Changes in _Indentation_ will influence _Line Length_.
3. Removal of _Line Breaks_ will influence _Line Length_ and may
   necessitate changes in _Spacing_.
4. Addition of _Line Breaks_ must take account of _Indentation_.
5. Resolving excessing _Line Length_ usually requires changes to
  _Line Breaks_ and potentially _Indentation_.

## Application in rules

### What is part of reflow and what is not?

In general there are two phases to a reflow related rule:
1. _Linting_ - working out whether there's an issue.
2. _Fixing_ - resolving the issue.

The intent is that _Fixing_ should always be in the reflow code.
_Linting_ may or may not be in the reflow code and could also be
encoded within the rule itself.

### How to apply in a rule context

When applying reflow in a rule context it makes sense to consider
how widespread the impact we want to have is:
- A rule designed around _Spacing_ may act in relative isolation,
  but may also optionally need to resolve excessive _Line Length_.
- A rule designed around _Indentation_ may act simply on it's own
  but may also optionally need to resolve excessive _Line Length_.
- A rule designed around the placement or presence of _Line Breaks_
  will probably have to consider _Spacing_ (or at least decide
  what spacing to impose at least for the moved elements) and if
  introducing additional _Line Breaks_ it may need to account
  for _Indentation_.
- Resolving _Line Length_ will involve introducing additional
  _Line Breaks_ (assuming that _Spacing_ has already been covered).

As a rule of thumb:
- If it's a rule about _Spacing_ it should only care about that
  in full knowledge that it may make lines too long. Unless the
  user has _also_ enabled long line checking, this is fine.
- If it's a rule about _Indentation_ we should also not check
  line length (for the same reasons).
- If it's a rule about _Line Breaks_ in relation to other segments
  (e.g. around commas or operators), we should aim to keep the
  existing _Indentation_ and not reset that or consider any
  _Line Length_ issues. We **should** consider _Spacing_, but
  only around the elements moved (e.g. if we're shifting a trailing
  comma to be a leading one, then we should also correct it's spacing
  at the same time).
- If it's a rule about _Line Length_ we will also need to consider
  _Indentation_ and _Line Breaks_.

### How to apply in a file reflow context

When reflowing a whole file we have a few considerations:
- Ideally we have all of the compulsory _Line Breaks_ and as few
  others as possible without going over our maximum _Line Length_,
  assuming correct _Indentation_ and _Spacing_.
- If additional _Line Breaks_ are required, we add them at the
  higher levels in the parse tree first before adding them deeper.

Therefore the order of operations should be:
1. Coerce the entire file to compulsory _Line Breaks_ **only**.
   i.e. Strip all non-compulsory ones, add in any missing
   compulsory ones.
2. Fix _Spacing_.
3. Fix _Indentation_.
4. Evaluate _Line Length_.
   a. If any lines are found too long. Add the next most appropriate
      _Line Break_ which shortens the offending line. Once added,
      re-fix _Indentation_ for the affected lines **only** (we should
      assume that if all we have done is add _Line Breaks_, i.e.
      convert `whitespace` to `newline`, that _Spacing_ should have
      no issues). Repeat step 4.
   b. If no lines are found too long, then we're good!

## Implications for configuration

To be able to both reflow whole files with knowledge of appropriate
_Spacing_ and _Line Breaks_, while also being able to lint effectively
in a rules context - we need to have a common way of defining what
our intended setup should be. On a very simple level, the understanding
that commas usually have whitespace after them, but not before, or that
bracket characters usually have whitespace outside them but not directly
inside them. On a more complex level, that we might want to configure
the precedence of operators in evaluating where to insert _Line Breaks_
in a long arithmetic expression. This naturally includes the
choice of whether to use trailing or leading commas.

The default configuration is that elements should be surrounded by a
single whitespace with no particular requirement around newlines.

All other configuration is a deviation from that default. Configuration
could live in two places:
1. On the segment definition in the dialect. This is a very helpful
   central place - and fits with the current location for indentation.
2. In a config file, either the central one (`.sqlfluff`), or a config
   file just for this purpose.

Given user requirements to be able to configure at least comma placement
the config file approach seems the most suitable - as it allows sensible
inheritance and deviation from a default spacing configuration.

### More specifically...

The configuration section as as `1.3.0` for indentation looks like this:

```ini
[sqlfluff:indentation]
# See https://docs.sqlfluff.com/en/stable/indentation.html
indented_joins = False
indented_ctes = False
indented_using_on = True
indented_on_contents = True
template_blocks_indent = True
```

I suggest that we introduce a new `layout` section of the config which has
roughly the following structure:

```ini
[sqlfluff:layout:type:comma]
spacing_before = False
line_break_relation = after  # default to trailing commas. For leading, specify "before"

[sqlfluff:layout:type:function_name]
spacing_after = False

[sqlfluff:layout:type:binary_operator]
line_break_relation = before  # default to operators at the start of lines, and not at the end

[sqlfluff:layout:type:start_bracket]
spacing_after = False

[sqlfluff:layout:type:end_bracket]
spacing_before = False

[sqlfluff:layout:type:start_square_bracket]
spacing_after = False

[sqlfluff:layout:type:end_square_bracket]
spacing_before = False

...
```

For now _Indentation_ control will stay where it is, but with _Spacing_ and
_Line Break_ control in new `layout` sections.
