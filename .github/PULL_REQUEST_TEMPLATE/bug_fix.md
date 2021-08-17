-- Firstly, thanks for fixing a bug! Secondly, please make sure your PR includes a test case demonstrating that the bug is fixed. Test cases should be as minimal as possible to show it's fixed but also be representative of the case the original reporter of the bug posted. If this PR is just a failing test case, please file it as a `draft` PR or use pytest `xfail` to mark the case as expected to fail. --

### Bug fix checklist
- [ ] I have identified the root cause of the bug.
- I have fixed:
  - [ ] All cases affected by the bug.
  - [ ] Some cases affected by the bug, but others still remain.
  - [ ] No cases, this PR just adds a failing test case.
- [ ] This PR includes test cases to demonstrate the fix. Specifically:
  - [ ] `.yml` rule test cases in `test/fixtures/rules/std_rule_cases`.
  - [ ] `.sql`/`.yml` parser test cases in `test/fixtures/parser`.
  - [ ] Full autofix test cases in `test/fixtures/linter/autofix`.
  - [ ] Other.

### What was the root cause of this bug?
...

### Are there any other side effects of this fix?
...

### How comprehensive is the test coverage of this fix?
...
