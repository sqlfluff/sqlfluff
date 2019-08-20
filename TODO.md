# TODO Notes


probably write some tests around identifier matching


the basic sql statement is ALMOST there, maybe simplify the grammar a bit before making it more complicated again.


Seperate out the matchResult class into a seperate module

## Notes

### Development (Now)
- deal with joins
- deal with insert statements and with statements
- deal with the infinite loop on the multi statement test
- deal with the infinite loop on the with statement test
- perf improvement on the sequence matcher to avoid testing more than once, do
  it in a single pass and work backwards from the end, if it doesn't match then
  we can immediately fail out.
### Development (Next)
- integrate with linting
- Implement config parsing from comment segments
### Pre Deployment
- Remove the TODO file or at least make this tidy before go-live
- Make a note about changes and limitations in the readme
