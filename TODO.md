# TODO Notes


probably write some tests around identifier matching


the basic sql statement is ALMOST there, maybe simplify the grammar a bit before making it more complicated again.


Seperate out the matchResult class into a seperate module

## Notes

### Development (Now)
- deal with joins
- deal with insert statements and with statements
- deal with the infinite loop on the multi statement test
- deal with the infinite loop on the with statement test (I think
  it's to do with not using a match result in _match_forward and maybe getting
  an n of 0)
- add some sensible matchers for the lower level building blocks (like identifiers)
  so that we reduce how deep the parser goes for certain things.
- *implement bracket counting on sequence matching?*
  - NO. The Bracketed Grammar needs to have it's own matcher which looks ahead
    using bracket counting to work out the exactly which elements should be matched.
    We then match on just them (no variable lengths).
- *implement a performance hack on sequence.* Allow grammars or matchers to report
  if they're a singleton, and therefore don't do the iterative match, just do a
  match on the first element.
- perf improvement on the sequence matcher to avoid testing more than once, do
  it in a single pass and work backwards from the end, if it doesn't match then
  we can immediately fail out.
### Development (Next)
- Implement config parsing from comment segments
- Implement some basic linting for:
  - consistent capitalisation of keywords
  - consistent capitalisation for unquoted identifiers
- Implement singleton matching for `::`, `:` and `||`. For the first two allow these
  in identifier matchers.
### Pre Deployment
- Remove the TODO file or at least make this tidy before go-live
- Make a note about changes and limitations in the readme
