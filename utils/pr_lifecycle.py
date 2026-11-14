"""Reconcile the lifecycle labels on pull requests.

This script is the single source of truth for the automated "lifecycle"
labels on pull requests (CI state, whose turn it is, open AI feedback, etc.).
It is intentionally state-based rather than event-based: given a PR, it
works out from the GitHub API which lifecycle labels *should* be present and
then applies the difference. Events (a push, a review, a CI run finishing)
only decide *which* PRs get reconciled; a scheduled sweep reconciles every open
PR so nothing can get stuck.

It only ever adds or removes the labels listed in ``MANAGED_LABELS`` (plus the
legacy ``awaiting feedback`` label on PRs). All other labels - dialects, bug,
enhancement, possible bot, etc. - are left alone.

The script uses only the standard library so that it can run from a bare
checkout of the default branch without installing anything. It is run by
``.github/workflows/pr-lifecycle.yml``, but can also be run locally::

    GITHUB_TOKEN=... python utils/pr_lifecycle.py --repo sqlfluff/sqlfluff --pr 1234
    GITHUB_TOKEN=... python utils/pr_lifecycle.py --repo sqlfluff/sqlfluff --all

Without ``--apply`` it only reports what it would change.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

# --- Label definitions -------------------------------------------------------

LABEL_FIRST_TIME = "pr: first-time contributor"
LABEL_STALE = "pr: stale"
LABEL_CI_NEEDS_APPROVAL = "ci: needs approval"
LABEL_CI_PASSING = "ci: passing"
LABEL_CI_FAILING = "ci: failing"
LABEL_AWAITING_AUTHOR = "review: awaiting author"
LABEL_AWAITING_MAINTAINER = "review: awaiting maintainer"
LABEL_AI_FEEDBACK_OPEN = "review: ai feedback open"

# name -> (colour, description). Used by ``--ensure-labels`` to create any
# that are missing, and as the definitive list of what this script manages.
MANAGED_LABELS: dict[str, tuple[str, str]] = {
    LABEL_FIRST_TIME: (
        "c2e0c6",
        "Opened by a first-time contributor. CI needs a maintainer's approval.",
    ),
    LABEL_CI_NEEDS_APPROVAL: (
        "e4e669",
        "CI is waiting for a maintainer to approve the workflow run.",
    ),
    LABEL_CI_PASSING: ("0e8a16", "CI is green on the latest commit."),
    LABEL_CI_FAILING: ("d93f0b", "CI is failing on the latest commit."),
    LABEL_AWAITING_AUTHOR: (
        "bfd4f2",
        "A maintainer has responded; waiting on the author.",
    ),
    LABEL_AWAITING_MAINTAINER: (
        "1d76db",
        "Waiting on a maintainer to review or respond.",
    ),
    LABEL_AI_FEEDBACK_OPEN: (
        "d4c5f9",
        "Has unresolved review threads opened by an AI reviewer.",
    ),
    LABEL_STALE: (
        "cccccc",
        "Waiting on the author with no activity for over 30 days.",
    ),
}

# Labels which this script replaces and will remove from PRs (but which are
# still used on issues, so are not renamed or deleted).
LEGACY_LABELS: frozenset[str] = frozenset({"awaiting feedback"})

# Workflows (by their ``name:``) which together decide the CI state of a PR.
CI_WORKFLOWS: frozenset[str] = frozenset({"CI", "pre-commit"})

FIRST_TIME_ASSOCIATIONS: frozenset[str] = frozenset(
    {"FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "NONE"}
)
MAINTAINER_ASSOCIATIONS: frozenset[str] = frozenset({"OWNER", "MEMBER"})

STALE_AFTER = timedelta(days=30)


# --- Pure decision logic -----------------------------------------------------


@dataclass
class WorkflowRun:
    """The bits of a workflow run we care about."""

    name: str
    status: str  # queued | in_progress | completed | ...
    conclusion: Optional[str]  # success | failure | action_required | ...


@dataclass
class PRState:
    """Everything needed to decide the lifecycle labels for one PR.

    This is deliberately a plain data structure so the decision logic in
    :func:`compute_desired_labels` can be unit tested without the API.
    """

    number: int
    is_open: bool
    is_draft: bool
    author_association: str
    labels: set[str]
    # The latest run of each CI workflow for the head commit.
    ci_runs: list[WorkflowRun] = field(default_factory=list)
    # Most recent push / comment / review from the PR author.
    last_author_activity: Optional[datetime] = None
    # Most recent (human) comment / review from a maintainer other than the
    # author.
    last_maintainer_activity: Optional[datetime] = None
    # Unresolved, non-outdated review threads whose first comment is by a bot.
    open_bot_threads: int = 0
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def _ci_labels(state: PRState) -> set[str]:
    """Work out the ``ci:`` labels for a PR."""
    runs = [run for run in state.ci_runs if run.name in CI_WORKFLOWS]
    if not runs:
        return set()
    if any(
        run.conclusion == "action_required" or run.status == "action_required"
        for run in runs
    ):
        return {LABEL_CI_NEEDS_APPROVAL}
    if any(run.status != "completed" for run in runs):
        # Still running: no claim either way.
        return set()
    conclusions = {run.conclusion for run in runs}
    if conclusions <= {"success", "skipped", "neutral"}:
        return {LABEL_CI_PASSING}
    if conclusions & {"failure", "timed_out", "startup_failure"}:
        return {LABEL_CI_FAILING}
    # Cancelled or otherwise inconclusive.
    return set()


def _review_labels(state: PRState) -> set[str]:
    """Work out whose court the ball is in.

    Drafts are never "awaiting maintainer" (the author is still working on
    them), but can be "awaiting author" if a maintainer spoke last.
    """
    author_last = state.last_maintainer_activity is None or (
        state.last_author_activity is not None
        and state.last_author_activity > state.last_maintainer_activity
    )
    if author_last:
        return set() if state.is_draft else {LABEL_AWAITING_MAINTAINER}
    return {LABEL_AWAITING_AUTHOR}


def compute_desired_labels(state: PRState) -> set[str]:
    """Return the set of managed labels which *should* be on the PR.

    Closed PRs are left untouched (an empty desired set would strip their
    history), so this returns the managed labels they already have.
    """
    if not state.is_open:
        return state.labels & set(MANAGED_LABELS)

    desired: set[str] = set()
    if state.author_association in FIRST_TIME_ASSOCIATIONS:
        desired.add(LABEL_FIRST_TIME)
    desired |= _ci_labels(state)
    desired |= _review_labels(state)
    if state.open_bot_threads:
        desired.add(LABEL_AI_FEEDBACK_OPEN)

    if LABEL_AWAITING_AUTHOR in desired:
        last_activity = max(
            (
                dt
                for dt in (state.last_author_activity, state.last_maintainer_activity)
                if dt is not None
            ),
            default=None,
        )
        if last_activity is not None and state.now - last_activity > STALE_AFTER:
            desired.add(LABEL_STALE)
    return desired


def label_diff(state: PRState) -> tuple[set[str], set[str]]:
    """Return ``(to_add, to_remove)`` for the PR."""
    desired = compute_desired_labels(state)
    managed = set(MANAGED_LABELS) | LEGACY_LABELS
    current = state.labels & managed
    return desired - current, current - desired


# --- GitHub API client --------------------------------------------------------


class GitHubClient:
    """A tiny stdlib-only client for the bits of the GitHub API we need."""

    api_url = "https://api.github.com"
    retries = 3  # On 5xx responses, with exponential backoff.

    def __init__(self, repo: str, token: str) -> None:
        self.repo = repo
        self.token = token

    def _request(
        self, method: str, url: str, body: Optional[dict[str, Any]] = None
    ) -> tuple[Any, dict[str, str]]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "sqlfluff-pr-lifecycle")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(req) as resp:
                    raw = resp.read()
                    headers = {k.lower(): v for k, v in resp.headers.items()}
                return (json.loads(raw) if raw else None), headers
            except urllib.error.HTTPError as err:
                detail = err.read().decode(errors="replace")
                if err.code >= 500 and attempt < self.retries:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError(f"{method} {url} -> {err.code}: {detail}") from err
        raise AssertionError("unreachable")  # pragma: no cover

    def rest(
        self,
        method: str,
        path: str,
        body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make a single REST call against this repo."""
        url = f"{self.api_url}/repos/{self.repo}/{path.lstrip('/')}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        result, _ = self._request(method, url, body)
        return result

    def paginate(
        self, path: str, params: Optional[dict[str, Any]] = None, key: str = ""
    ) -> Iterator[Any]:
        """Iterate over every item of a paginated REST list endpoint."""
        params = {"per_page": 100, **(params or {})}
        url: Optional[str] = (
            f"{self.api_url}/repos/{self.repo}/{path.lstrip('/')}?"
            + urllib.parse.urlencode(params)
        )
        while url:
            page, headers = self._request("GET", url)
            items = page[key] if key else page
            yield from items
            url = None
            for part in headers.get("link", "").split(","):
                if 'rel="next"' in part:
                    url = part[part.index("<") + 1 : part.index(">")]

    def graphql(self, query: str, variables: dict[str, Any]) -> Any:
        """Make a GraphQL call."""
        result, _ = self._request(
            "POST", f"{self.api_url}/graphql", {"query": query, "variables": variables}
        )
        if result.get("errors"):
            raise RuntimeError(f"GraphQL error: {result['errors']}")
        return result["data"]


# --- Gathering state from the API --------------------------------------------


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _is_bot(user: Optional[dict[str, Any]]) -> bool:
    if not user:
        return True
    return user.get("type") == "Bot" or str(user.get("login", "")).endswith("[bot]")


def _latest(current: Optional[datetime], new: Optional[datetime]) -> Optional[datetime]:
    if new is None:
        return current
    if current is None or new > current:
        return new
    return current


def _earliest(
    current: Optional[datetime], new: Optional[datetime]
) -> Optional[datetime]:
    if new is None:
        return current
    if current is None or new < current:
        return new
    return current


_THREADS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          comments(first: 1) { nodes { author { __typename login } } }
        }
      }
    }
  }
}
"""


def _count_open_bot_threads(client: GitHubClient, number: int) -> int:
    owner, repo = client.repo.split("/", 1)
    cursor: Optional[str] = None
    count = 0
    while True:
        data = client.graphql(
            _THREADS_QUERY,
            {"owner": owner, "repo": repo, "number": number, "cursor": cursor},
        )
        threads = data["repository"]["pullRequest"]["reviewThreads"]
        for thread in threads["nodes"]:
            if thread["isResolved"] or thread["isOutdated"]:
                continue
            comments = thread["comments"]["nodes"]
            author = comments[0]["author"] if comments else None
            if author is None or author["__typename"] == "Bot":
                count += 1
        if not threads["pageInfo"]["hasNextPage"]:
            return count
        cursor = threads["pageInfo"]["endCursor"]


def _ci_runs_for_sha(
    client: GitHubClient, sha: str
) -> tuple[list[WorkflowRun], Optional[datetime]]:
    """Latest run of each CI workflow for a commit, and when the first started.

    The first run is created when the commit is pushed, so its start time is the
    push time, unlike the commit's own date which is when it was made.
    """
    runs = client.rest(
        "GET", "actions/runs", params={"head_sha": sha, "per_page": 100}
    )["workflow_runs"]
    latest: dict[str, dict[str, Any]] = {}
    first_created: Optional[datetime] = None
    for run in runs:  # Newest first.
        if run["event"] != "pull_request" or run["name"] not in CI_WORKFLOWS:
            continue
        latest.setdefault(run["name"], run)
        first_created = _earliest(first_created, _parse_dt(run["created_at"]))

    return [
        WorkflowRun(r["name"], r["status"], r["conclusion"]) for r in latest.values()
    ], first_created


def gather_state(client: GitHubClient, number: int) -> PRState:
    """Collect everything :func:`compute_desired_labels` needs for one PR."""
    pr = client.rest("GET", f"pulls/{number}")
    author_login = pr["user"]["login"]
    state = PRState(
        number=number,
        is_open=pr["state"] == "open",
        is_draft=bool(pr["draft"]),
        author_association=pr["author_association"],
        labels={label["name"] for label in pr["labels"]},
    )
    if not state.is_open:
        return state

    state.ci_runs, pushed_at = _ci_runs_for_sha(client, pr["head"]["sha"])

    # The head commit is the author's most recent push (whoever committed it).
    # The commit date is when it was made, which can be well before it was
    # pushed, so prefer the time its first CI run started.
    head = client.rest("GET", f"commits/{pr['head']['sha']}")
    state.last_author_activity = _latest(
        _parse_dt(head["commit"]["committer"]["date"]), pushed_at
    )

    activity: Iterable[tuple[dict[str, Any], str, Optional[str]]] = (
        *(
            (c, c["author_association"], c["created_at"])
            for c in client.paginate(f"issues/{number}/comments")
        ),
        *(
            (c, c["author_association"], c["created_at"])
            for c in client.paginate(f"pulls/{number}/comments")
        ),
        *(
            (r, r["author_association"], r["submitted_at"])
            for r in client.paginate(f"pulls/{number}/reviews")
            if r["state"] != "PENDING"
        ),
    )
    for item, association, timestamp in activity:
        user = item["user"]
        when = _parse_dt(timestamp)
        if _is_bot(user):
            continue
        if user["login"] == author_login:
            state.last_author_activity = _latest(state.last_author_activity, when)
        elif association in MAINTAINER_ASSOCIATIONS:
            state.last_maintainer_activity = _latest(
                state.last_maintainer_activity, when
            )

    state.open_bot_threads = _count_open_bot_threads(client, number)
    return state


# --- Applying -----------------------------------------------------------------


def reconcile(
    client: GitHubClient, number: int, apply: bool
) -> tuple[set[str], set[str]]:
    """Reconcile one PR, returning what was (or would be) added and removed."""
    state = gather_state(client, number)
    to_add, to_remove = label_diff(state)
    if apply:
        if to_add:
            client.rest("POST", f"issues/{number}/labels", {"labels": sorted(to_add)})
        for label in sorted(to_remove):
            client.rest("DELETE", f"issues/{number}/labels/{urllib.parse.quote(label)}")
    return to_add, to_remove


def ensure_labels(client: GitHubClient, apply: bool) -> list[str]:
    """Create any managed labels which don't exist yet. Returns the created."""
    existing = {label["name"] for label in client.paginate("labels")}
    created = []
    for name, (color, description) in MANAGED_LABELS.items():
        if name in existing:
            continue
        created.append(name)
        if apply:
            client.rest(
                "POST",
                "labels",
                {"name": name, "color": color, "description": description},
            )
    return created


def resolve_targets(
    client: GitHubClient, event_name: str, event: dict[str, Any]
) -> list[int]:
    """Work out which PRs an event should trigger a reconcile for."""
    if "pull_request" in event and isinstance(event["pull_request"], dict):
        return [int(event["pull_request"]["number"])]
    if event_name == "issue_comment":
        issue = event.get("issue", {})
        return [int(issue["number"])] if "pull_request" in issue else []
    if event_name == "workflow_run":
        # ``workflow_run.pull_requests`` is empty for PRs from forks, so look
        # the PR up from the commit instead.
        sha = event["workflow_run"]["head_sha"]
        return [
            int(pr["number"])
            for pr in client.paginate(f"commits/{sha}/pulls")
            if pr["state"] == "open"
        ]
    # schedule, workflow_dispatch without a number, or anything unexpected:
    # sweep everything.
    return [int(pr["number"]) for pr in client.paginate("pulls", {"state": "open"})]


# --- CLI ----------------------------------------------------------------------


def _parse_args(argv: Optional[list[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/name (default: $GITHUB_REPOSITORY)",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--pr", type=int, action="append", help="PR number(s)")
    target.add_argument("--all", action="store_true", help="every open PR")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually change labels (default is a dry run)",
    )
    parser.add_argument(
        "--ensure-labels",
        action="store_true",
        help="create any managed labels which are missing from the repo",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point."""
    args = _parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN")
    if not args.repo or not token:
        print("Both --repo (or $GITHUB_REPOSITORY) and $GITHUB_TOKEN are required.")
        return 2
    client = GitHubClient(args.repo, token)
    mode = "APPLY" if args.apply else "DRY RUN"
    lines: list[str] = [f"PR lifecycle labels ({mode})", ""]

    if args.ensure_labels:
        created = ensure_labels(client, args.apply)
        if created:
            lines.append(f"Created labels: {', '.join(created)}")
        else:
            lines.append("All managed labels already exist.")
        lines.append("")

    if args.pr:
        numbers = args.pr
    elif args.all:
        numbers = resolve_targets(client, "schedule", {})
    else:
        event_name = os.environ.get("GITHUB_EVENT_NAME", "")
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        event: dict[str, Any] = {}
        if event_path and os.path.exists(event_path):
            with open(event_path, encoding="utf-8") as f:
                event = json.load(f)
        numbers = resolve_targets(client, event_name, event)

    for number in numbers:
        to_add, to_remove = reconcile(client, number, args.apply)
        if to_add or to_remove:
            adds = " ".join(f"+[{label}]" for label in sorted(to_add))
            removes = " ".join(f"-[{label}]" for label in sorted(to_remove))
            lines.append(f"#{number}: {adds} {removes}".rstrip())
        else:
            lines.append(f"#{number}: no change")

    output = "\n".join(lines)
    print(output)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(output.replace("\n", "\n\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
