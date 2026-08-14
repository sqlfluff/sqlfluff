# How to use Git

Many contributors may not be familiar with Git — it can be a confusing world
for those new to it, with perplexing terms like _clone_, _fork_, _branch_,
_merge conflicts_, and _rebase_. This guide provides some background for those
new to Git, and also serves as a quick reference for terms and commands used in
the SQLFluff contribution workflow.

## Introduction to Git

This section gives some basic background for complete Git newcomers. If you
already understand the basics, skip to
[Recommended way to use Git for SQLFluff](#recommended-way-to-use-git-for-sqlfluff).

### What is Git?

Git is a _distributed version control system_. That mouthful basically means
it's a way of keeping track of changes to source code — especially when many
people are changing various parts of it simultaneously. The _distributed_ part
is what makes Git so interesting (and so complicated!): there can be many copies
of the code, and keeping them in sync can get complex.

The original copy of a codebase (called a _repository_ or _repo_) is hosted on
a server (e.g. GitHub). People work on copies locally, or may have _forked_ the
repo to their own GitHub account — and then cloned that fork locally too. Add
in different branches across any of those copies and it can get quite confusing.

### What is GitHub and how is it different from Git?

GitHub is not Git, but it is one of the most commonly used Git hosting services.
The main things GitHub gives you are a Git server to store your code and a nice
web interface to manage it. Through the web interface you can view and edit code,
raise issues, open and review pull requests, use GitHub Actions to automate
tasks, and more.

SQLFluff makes extensive use of GitHub to manage the project and allow
contributors to collaborate. Other similar services include GitLab and BitBucket.

GitHub also provides a graphical desktop app called
[GitHub Desktop](https://desktop.github.com/) — see the
[GitHub Desktop](#github-desktop) section for tips.

### Installing Git

While it's possible to contribute using only GitHub's website, working locally
is much more practical. Git is widely available — see the
[installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
for Windows, Mac, and Linux.

To check if Git is already installed, open a terminal and run:

```bash
git --version
```

If you see a version number, you're ready. If not:

- **Windows**: Install [Git Bash](https://git-scm.com/download/win) for a
  Linux-like command line experience.
- **macOS**: Running the version check will prompt you to install Xcode and Git.
- **Linux**: Install via your package manager.

### Git Repos

A Git _repository_ (or _repo_) is a collection of all the code that makes up a
project. The main SQLFluff repo is at https://github.com/sqlfluff/sqlfluff.
Additional repos for extensions and tooling are at https://github.com/sqlfluff.

### Git Branches

A repo typically contains many branches — independent lines of development where
you can work without affecting others. Like a tree, branches diverge from each
other, but unlike a tree they are usually merged back when work is complete.

One branch is the primary one (SQLFluff uses `main`) into which everything is
eventually merged. Creating a branch is quick and cheap — Git stores only
differences, not full copies. Working in small, focused branches that are merged
frequently is the best practice.

### GitHub Pull Requests

Once changes are ready, you open a _pull request_ (PR) — a GitHub feature that
creates a structured merge request. A PR has several tabs:

- **Conversation** — description, comments, and review discussion.
- **Commits** — individual commits in the change.
- **Checks** — automated tests and CI results.
- **Files Changed** — a line-by-line diff; reviewers can comment on individual
  lines and suggest code changes directly.

![Screenshot of an example pull request on GitHub.](/images/git/github_example_pr.png)

At the bottom of the Conversation tab, when checks pass and the PR is approved,
you'll see the merge button:

![Bottom of a pull request showing the Squash and Merge button.](/images/git/github_example_merge_panel.png)

Clicking **Squash and Merge** merges all commits as one, which keeps the history
clean. You do **not** need to close and reopen a PR when addressing review
feedback — simply push changes to the branch and the PR updates automatically.

### GitHub Forks

A _fork_ is a complete copy of a repo in your own GitHub account. You create a
branch in your fork, make changes, and then open a PR from your fork back to the
original (_upstream_) repo. Most SQLFluff contributors work this way because only
core maintainers can create branches directly in the main repo.

::: info About the term "fork"
Traditionally, "fork" meant taking a project in a different direction
permanently. On GitHub, a fork is typically used to make changes with the
intention of merging them back into the original repo.
:::

Key terminology to keep straight:

- **upstream** — the original SQLFluff repo (`github.com/sqlfluff/sqlfluff`)
- **origin** — your fork on GitHub
- **local** — the copy on your machine

Forks must be kept in sync with the upstream repo periodically — we explain how
below.

### Cloning a Git Repo

To work locally, you _clone_ a repo — downloading a copy to your machine. Clone
your fork (not the main repo) so you can push changes back to it:

![Screenshot of the clone button in GitHub.](/images/git/github_clone_button.png)

Options:

- **Clone with SSH** — recommended; requires [SSH key setup](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
  but avoids entering your password each time.
- **Clone with HTTPS** — simpler setup but requires a password (or personal
  access token) on each push.

```bash
# SSH (recommended)
git clone git@github.com:YOUR_USERNAME/sqlfluff.git

# HTTPS
git clone https://github.com/YOUR_USERNAME/sqlfluff.git
```

### Git Merge Conflicts

When keeping copies in sync, you will inevitably encounter _merge conflicts_ —
when you and someone else have both changed the same line. Git flags these and
asks you to resolve them manually. A conflicted file looks like this:

```
If you have questions, please
<<<<<<< HEAD
open an issue
=======
ask your question in Slack
>>>>>>> branch-a
```

To resolve: decide which version you want, delete the other version and all the
`<<<<`, `====`, and `>>>>` markers, then `git add` the resolved file.

Merge conflicts have a scary reputation but are usually straightforward to
resolve. The best way to reduce them is to sync your branch with `main`
frequently and keep PRs small and focused.

---

## Recommended way to use Git for SQLFluff

### Initial setup

1. Click the **Fork** button on the SQLFluff GitHub page.

2. Clone your fork locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/sqlfluff.git
   cd sqlfluff
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream git@github.com:sqlfluff/sqlfluff.git
   ```

It is **strongly** recommended **not** to work directly on the `main` branch of
your fork. Keep `main` clean so you can always create fresh branches from it.

### Resyncing your main branch to upstream

To keep your fork's `main` in sync with upstream, the cleanest approach is a
hard reset. This discards any changes you have on `main` — which should be none
if you follow the advice above.

::: warning
Only do this if you have no in-flight changes on your `main` branch.
:::

```bash
# Check what remotes you have
git remote -v

# Add upstream if not already added
git remote add upstream git@github.com:sqlfluff/sqlfluff.git

# Reset your main to match upstream exactly
git fetch upstream
git checkout main
git reset --hard upstream/main
git push origin main --force
```

Afterwards, visit your fork on GitHub and confirm you see:
_"This branch is even with sqlfluff:main."_

![A forked repo which is even with upstream.](/images/git/github_fork_status.png)

### Creating and working on a branch

1. Resync `main` to upstream (unless you just forked).
2. Check out `main`: `git checkout main`
3. Create a branch with a meaningful name:
   ```bash
   git checkout -b postgres-create-table
   ```
4. Make your changes in your editor.
5. Test your changes — see [CONTRIBUTING.md](https://github.com/sqlfluff/sqlfluff/blob/main/CONTRIBUTING.md)
   for setup instructions and the relevant `tox` commands.
6. Stage any new files:
   ```bash
   git add path/to/new/file.sql
   ```
7. Commit your changes:
   ```bash
   git commit -a -m "Add Postgres CREATE TABLE support"
   ```
8. Push to GitHub:
   ```bash
   git push
   # First push of a new branch needs:
   git push --set-upstream origin postgres-create-table
   ```
9. If others have pushed to the same branch, pull their changes first:
   ```bash
   git pull
   ```
10. Repeat steps 4–9 until ready to open a pull request.

### Keeping your branch up to date

Before opening a PR — and periodically while working — merge changes from
upstream `main` into your branch:

```bash
git fetch upstream
git merge upstream/main
git push
```

If there were merge conflicts, Git will pause and ask you to resolve them. Once you've resolved the conflicts and staged the affected files with `git add`, run `git commit` to complete the merge, then `git push`.

### Switching between branches

Git lets you work on several branches at once:

```bash
# Start feature1
git checkout main && git pull
git checkout -b feature1
# ... make commits ...
git push --set-upstream origin feature1

# Switch to a new branch while waiting for feedback on feature1
git checkout main && git pull
git checkout -b feature2
# ... make commits ...
git push --set-upstream origin feature2

# Come back to feature1
git checkout feature1
```

Use `git status` frequently to confirm which branch you're on and that all
changes are committed before switching.

### Opening a Pull Request

1. Merge in any upstream `main` changes since you branched.
2. Run the tests locally (see CONTRIBUTING.md for the `tox` command).
3. Push all commits to GitHub.
4. Go to the SQLFluff repo on GitHub and open a pull request.
5. If the PR closes an issue, add `Closes #123` or `Fixes #123` in the
   description — GitHub will close it automatically on merge. If it partially
   addresses an issue, use `Makes progress on #123` instead.

You can keep pushing to your branch after the PR is open — the PR updates
automatically and checks rerun. There is no need to close and reopen.

### Responding to review feedback

**Automated checks** run first. A green tick means all checks passed; a red
cross means something needs fixing. Look at the check details to understand
what failed.

**Merge conflict checks** are done by GitHub itself. Keeping your branch
synced with `main` before opening the PR minimises these.

**Linting checks** run automatically. You can replicate them locally with
`pre-commit run --all-files`.

**Code review feedback** comes from a maintainer or contributor. Treat review
as an opportunity to improve — it is not a personal criticism. If a reviewer
makes a code suggestion directly on GitHub, you can accept it in one click (then
`git pull` locally to get the changes). After addressing all feedback, re-request
a review by clicking the icon next to the reviewer's name, or leave a comment to
signal you're ready.

::: info Draft pull requests
Open a draft PR early if you want feedback on your approach before finishing.
Remember to convert to a full PR when ready.
:::

### Reviewing pull requests

We **strongly** encourage contributors to review pull requests — this is a
collaborative effort and depending on one or two people creates a bottleneck.

- Even if a review finds nothing, an approval is valuable — it confirms the PR
  has had a second pair of eyes.
- Be mindful that many contributors are new to the codebase (or to English) —
  avoid jargon and colloquialisms.
- Remember that `Perfect is the enemy of good` — an incremental improvement that
  can be merged is often better than waiting for the perfect solution.
- Use positive GitHub reactions (❤️, 🚀) for quick encouragement, especially for
  new contributors. Avoid the negative ones (👎, 😕) — use a comment instead to
  explain concerns clearly.

![GitHub Heart and Rocket reactions.](/images/git/github_reactions.png)

---

## GitHub Desktop

GitHub Desktop is a Windows and macOS app that provides a visual interface for
Git, reducing the need to use the command line.

### Installing GitHub Desktop

First make sure you have Git installed (see [Installing Git](#installing-git)).
Then download from https://desktop.github.com/ and follow the
[setup instructions](https://docs.github.com/en/free-pro-team@latest/desktop/installing-and-configuring-github-desktop)
including authenticating with GitHub and configuring your identity.

### Cloning the SQLFluff repo

Follow
[Cloning a repository from GitHub to GitHub Desktop](https://docs.github.com/en/free-pro-team@latest/desktop/contributing-and-collaborating-using-github-desktop/cloning-a-repository-from-github-to-github-desktop):
go to your fork on GitHub and select **Open with GitHub Desktop**.

### Basic workflow

- **Current repository** toolbar button — switch between repos.
- **Pull origin** — fetch and merge any upstream changes.
- **Create a branch** — click the "Current branch" tab, type a name, click
  "Create new branch". Always branch from `main` and make sure `main` is
  up to date first.
- **Committing** — fill in the summary field in the bottom-left panel and click
  **Commit to `branch-name`**.
- **Publishing / pushing** — GitHub Desktop will prompt you to push after
  committing.
- **Opening a PR** — go to the SQLFluff repo on GitHub, select your branch, and
  click **Pull request**.

Keep your fork's `main` in sync with upstream before creating any new branches
(see [Resyncing your main branch to upstream](#resyncing-your-main-branch-to-upstream)).

---

## Glossary of Git terms

| Term | Definition |
|------|-----------|
| **branch** | An independent line of development within a repo. |
| **clone** | A local copy of a repo. |
| **fetch** | Download changes from a remote repo without merging them. |
| **fork** | A copy of a repo in your own GitHub account. |
| **LGTM** | "Looks Good To Me" — commonly used when approving a PR. |
| **local** | The copy of a repo on your machine. |
| **main** | The primary branch of the SQLFluff repo. |
| **merge** | Combining changes from one branch into another. |
| **merge request** | What GitLab calls a pull request. |
| **origin** | Your fork on GitHub (the remote your local clone pushes to). |
| **pull** | Fetch changes from a remote and merge them in one step. |
| **pull request (PR)** | A GitHub mechanism to propose and review a merge into the main repo. |
| **push** | Send local commits to a remote repo. |
| **rebase** | Reapply your commits on top of another branch's history. |
| **repo / repository** | A git project — a collection of versioned files. |
| **upstream** | The original SQLFluff repo that your fork was created from. |
