# TODO Notes


probably write some tests around identifier matching


the basic sql statement is ALMOST there, maybe simplify the grammar a bit before making it more complicated again.


Seperate out the matchResult class into a seperate module

## Notes

### Development (Now)
- deal with joins
  - Use `sqlfluff lint test/fixtures/cli/passing_b.sql -vv` for testing
- deal with insert statements
- add some sensible matchers for the lower level building blocks (like identifiers)
  so that we reduce how deep the parser goes for certain things.
- Fix all the now-failing tests
### Development (Next)
- Implement config parsing from comment segments
- Implement some basic linting for:
  - consistent capitalisation of keywords
  - consistent capitalisation for unquoted identifiers
- Implement singleton matching for `::`, `:` and `||`. For the first two allow these
  in identifier matchers.
- Hook up dialects
- Add some tests for lots of the new bits (especially rules)
- Implement a context manager for all the parse and match depth details.
### Pre Deployment
- Remove the TODO file or at least make this tidy before go-live
- Make a note about changes and limitations in the readme
- UPDATE CLI docs for all the existing methods and their commands.
- Implement all the old rules
