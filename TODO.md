## TODO

### Development (Now)
- deal with insert statements
- Fix all the now-failing tests
- Implement proper matching for join conditions
### Development (Next)
- Implement config parsing from comment segments
- Implement some basic linting for:
  - Most of the original linting rules
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

### Things to put up for hacktober fest (or starter things)
- Update docs to represent current implementation
- Update the readouts from functions to match current state in the docs.
- More crawlers
- Blacklisting
- Better dialect handling
