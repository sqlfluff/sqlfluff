# Using [GitHub Actions](https://github.com/features/actions) to Annotate PRs

There are two way to utilize SQLFluff to annotate Github PRs.

1. When `sqlfluff lint` is run with the `--format github-annotation-native`
   option, it produces output formatted as [Github workflow commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-a-notice-message) which
   are converted into pull request annotations by Github.

2. When `sqlfluff lint` is run with the `--format github-annotation`
   option, it produces output compatible with this [action from yuzutech](https://github.com/yuzutech/annotations-action).
   Which uses Github API to annotate the SQL in [GitHub pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

::: warning WARNING
At present (December 2023), limitations put in place by Github mean that only the
first 10 annotations will be displayed if the first option (using
`github-annotation-native`) is used. This is a not something that SQLFluff
can control itself and so we currently recommend using the the second option
above and the [action from yuzutech](https://github.com/yuzutech/annotations-action).

There is an [open feature request](https://github.com/orgs/community/discussions/68471)
for GitHub Actions which you can track to follow this issue.
:::

For more information and examples on using SQLFluff in GitHub Actions, see the
[sqlfluff-github-actions repository](https://github.com/sqlfluff/sqlfluff-github-actions).
