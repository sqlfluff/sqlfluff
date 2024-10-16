# SQLFluff ignore file tests

In this folder there are five queries. Only one of them should be
found as the others are all covered by various ignore files.

* `path_a/query_a.sql` is ignored by the root `.sqlfluffignore`,
  by ignoring the whole of `path_a/`.
* `path_b/query_b.sql` is *not ignored*.
* `path_b/query_c.sql` is ignored by name in `path_b/.sqlfluffignore`.
* `path_b/query_d.sql` is ignored by name in `path_b/.sqlfluff`.
* `path_c/query_e.sql` is ignored by the `pyproject.toml` config
  file which ignores the whole of `path_c/`.
