
<!--Thanks for adding this feature!-->

<!--Please give the Pull Request a meaningful title for the release notes-->

### Brief summary of the change made
<!--Please include `fixes #XXXX` to automatically close any corresponding issue when the pull request is merged. Alternatively if not fully closed you can say `makes progress on #XXXX`.-->


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
