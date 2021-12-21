
<!--Firstly, thanks for adding this feature! Secondly, please check the key steps against the checklist below to make your contribution easy to merge.-->

<!--Please give the Pull Request a meaningful title (including the dialect this PR is for if it is dialect specific), as this will automatically be added to the release notes, and then the Change Log.-->

### Brief summary of the change made
<!--If there is an open issue for this, then please include `fixes #XXXX` or `closes #XXXX` replacing `XXXX` with the issue number and it will automatically close the issue when the pull request is merged. Alternatively if not fully closed you can say `makes progress on #XXXX` to create a link on that issue without closing it.-->


### Are there any other side effects of this change that we should be aware of?


### Pull Request checklist
- [ ] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes, which may be one or more of the following:
  - `.yml` rule test cases in `test/fixtures/rules/std_rule_cases`.
  - `.sql`/`.yml` parser test cases in `test/fixtures/dialects` (note YML files can be auto generated with `tox -e generate-fixture-yml`).
  - Full autofix test cases in `test/fixtures/linter/autofix`.
  - Other.
- Added appropriate documentation for the change.
- Created GitHub issues for any relevant followup/future enhancements if appropriate.
