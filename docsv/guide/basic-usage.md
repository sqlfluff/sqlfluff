# Basic Usage

To get a feel for how to use *SQLFluff* it helps to have a small
`.sql` file which has a simple structure and some known
issues for testing. Create a file called `test.sql` in the
same folder that you're currently in with the following content:

```sql
SELECT a+b  AS foo,
c AS bar from my_table
```

You can then run `sqlfluff lint test.sql --dialect ansi` to lint this
file.

```bash

$ sqlfluff lint test.sql --dialect ansi
== [test.sql] FAIL
L:   1 | P:   1 | LT09 | Select targets should be on a new line unless there is
                        | only one select target.
                        | [layout.select_targets]
L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                        | and aggregates. [structure.column_order]
L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                        | [layout.indent]
L:   1 | P:   9 | LT01 | Expected single whitespace between naked identifier and
                        | binary operator '+'. [layout.spacing]
L:   1 | P:  10 | LT01 | Expected single whitespace between binary operator '+'
                        | and naked identifier. [layout.spacing]
L:   1 | P:  11 | LT01 | Expected only single space before 'AS' keyword. Found '
                        | '. [layout.spacing]
L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                        | [layout.indent]
L:   2 | P:   9 | LT02 | Expected line break and no indent before 'from'.
                        | [layout.indent]
L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                        | [capitalisation.keywords]
All Finished 📜 🎉!
```

You'll see that *SQLFluff* has failed the linting check for this file.
On each of the following lines you can see each of the problems it has
found, with some information about the location and what kind of
problem there is. One of the errors has been found on *line 1*, *position *
(as shown by `L:   1 | P:   9`) and it's a problem with rule
*LT01* (for a full list of rules, see [Rule Reference](../reference/rules/index)). From this
(and the following error) we can see that the problem is that there
is no space either side of the `+` symbol in `a+b`.
Head into the file, and correct this issue so that the file now
looks like this:

```sql

SELECT a + b  AS foo,
c AS bar from my_table
```

Rerun the same command as before, and you'll see that the original
error (violation of *LT01*) no longer shows up.

```bash

$ sqlfluff lint test.sql --dialect ansi
== [test.sql] FAIL
L:   1 | P:   1 | LT09 | Select targets should be on a new line unless there is
                        | only one select target.
                        | [layout.select_targets]
L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                        | and aggregates. [structure.column_order]
L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                        | [layout.indent]
L:   1 | P:  13 | LT01 | Expected only single space before 'AS' keyword. Found '
                        | '. [layout.spacing]
L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                        | [layout.indent]
L:   2 | P:   9 | LT02 | Expected line break and no indent before 'from'.
                        | [layout.indent]
L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                        | [capitalisation.keywords]
```

To fix the remaining issues, we're going to use one of the more
advanced features of *SQLFluff*, which is the *fix* command. This
allows more automated fixing of some errors, to save you time in
sorting out your sql files. Not all rules can be fixed in this way
and there may be some situations where a fix may not be able to be
applied because of the context of the query, but in many simple cases
it's a good place to start.

For now, we only want to fix the following rules: *LT02*, *LT12*, *CP01*

```bash
$ sqlfluff fix test.sql --rules LT02,LT12,CP01 --dialect ansi
==== finding violations ====
== [test.sql] FAIL
L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                        | [layout.indent]
L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                        | [layout.indent]
L:   2 | P:   9 | LT02 | Expected line break and no indent before 'FROM'.
                        | [layout.indent]
L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                        | [capitalisation.keywords]
==== fixing violations ====
4 fixable linting violations found
Are you sure you wish to attempt to fix these? [Y/n]
```

...at this point you'll have to confirm that you want to make the
changes by pressing `y` on your keyboard...

```bash
Are you sure you wish to attempt to fix these? [Y/n] ...
Attempting fixes...
Persisting Changes...
== [test.sql] PASS
Done. Please check your files to confirm.
```

If we now open up `test.sql`, we'll see the content is
now different.

```sql
SELECT
    a + b  AS foo,
    c AS bar
FROM my_table
```

In particular:

* The two columns have been indented to reflect being inside the
  `SELECT` statement.
* The `FROM` keyword has been capitalised to match the
  other keywords.

We could also fix *all* of the fixable errors by not
specifying `--rules`.

```bash
$ sqlfluff fix test.sql --dialect ansi
==== finding violations ====
== [test.sql] FAIL
L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                    | and aggregates. [structure.column_order]
L:   2 | P:  10 | LT01 | Expected only single space before 'AS' keyword. Found '
                    | '. [layout.spacing]
==== fixing violations ====
2 fixable linting violations found
Are you sure you wish to attempt to fix these? [Y/n] ...
Attempting fixes...
Persisting Changes...
== [test.sql] PASS
Done. Please check your files to confirm.
```

If we now open up `test.sql`, we'll see the content has
been updated again.

```sql
SELECT
    c AS bar,
    a + b AS foo
FROM my_table
```

The SQL statement is now well formatted according to all the
rules defined in SQLFluff.

The `--rules` argument is optional, and could be useful when
you or your organisation follows a slightly different convention
than what we have defined.
