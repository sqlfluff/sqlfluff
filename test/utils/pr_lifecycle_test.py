"""Tests for the PR lifecycle label reconciler."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

from utils.pr_lifecycle import (
    LABEL_AI_FEEDBACK_OPEN,
    LABEL_AWAITING_AUTHOR,
    LABEL_AWAITING_MAINTAINER,
    LABEL_CI_FAILING,
    LABEL_CI_NEEDS_APPROVAL,
    LABEL_CI_PASSING,
    LABEL_FIRST_TIME,
    LABEL_STALE,
    PRState,
    WorkflowRun,
    _ci_runs_for_sha,
    compute_desired_labels,
    ensure_labels,
    label_diff,
    resolve_targets,
)

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)


def _state(**kwargs: Any) -> PRState:
    defaults: dict[str, Any] = dict(
        number=1,
        is_open=True,
        is_draft=False,
        author_association="CONTRIBUTOR",
        labels=set(),
        now=NOW,
    )
    defaults.update(kwargs)
    return PRState(**defaults)


def _runs(ci: Optional[str], precommit: Optional[str] = "success") -> list[WorkflowRun]:
    """Build CI + pre-commit runs. ``None`` means 'still running'."""
    return [
        WorkflowRun("CI", "completed" if ci else "in_progress", ci),
        WorkflowRun(
            "pre-commit", "completed" if precommit else "in_progress", precommit
        ),
    ]


@pytest.mark.parametrize(
    "state,expected",
    [
        # Nothing has happened yet: it's on us.
        (_state(), {LABEL_AWAITING_MAINTAINER}),
        # First time contributor, CI waiting for approval.
        (
            _state(
                author_association="FIRST_TIME_CONTRIBUTOR",
                ci_runs=_runs("action_required", "action_required"),
            ),
            {LABEL_FIRST_TIME, LABEL_CI_NEEDS_APPROVAL, LABEL_AWAITING_MAINTAINER},
        ),
        # Approval-gated runs can also report it as their status.
        (
            _state(
                author_association="FIRST_TIME_CONTRIBUTOR",
                ci_runs=[
                    WorkflowRun("CI", "action_required", None),
                    WorkflowRun("pre-commit", "completed", "success"),
                ],
            ),
            {LABEL_FIRST_TIME, LABEL_CI_NEEDS_APPROVAL, LABEL_AWAITING_MAINTAINER},
        ),
        # "NONE" association also counts as a first timer.
        (
            _state(author_association="NONE"),
            {LABEL_FIRST_TIME, LABEL_AWAITING_MAINTAINER},
        ),
        # CI green.
        (
            _state(ci_runs=_runs("success")),
            {LABEL_CI_PASSING, LABEL_AWAITING_MAINTAINER},
        ),
        # CI still running: no CI label at all.
        (_state(ci_runs=_runs(None)), {LABEL_AWAITING_MAINTAINER}),
        # Only one of the two workflows finished: still no CI label.
        (_state(ci_runs=_runs("success", None)), {LABEL_AWAITING_MAINTAINER}),
        # pre-commit failing is a CI failure too.
        (
            _state(ci_runs=_runs("success", "failure")),
            {LABEL_CI_FAILING, LABEL_AWAITING_MAINTAINER},
        ),
        # Cancelled runs are inconclusive.
        (_state(ci_runs=_runs("cancelled")), {LABEL_AWAITING_MAINTAINER}),
        # CI failing.
        (
            _state(ci_runs=_runs("failure")),
            {LABEL_CI_FAILING, LABEL_AWAITING_MAINTAINER},
        ),
        # Runs from workflows we don't track are ignored.
        (
            _state(ci_runs=[WorkflowRun("AgentScan", "completed", "failure")]),
            {LABEL_AWAITING_MAINTAINER},
        ),
        # A maintainer responded most recently: waiting on the author.
        (
            _state(
                last_author_activity=NOW - timedelta(days=2),
                last_maintainer_activity=NOW - timedelta(days=1),
            ),
            {LABEL_AWAITING_AUTHOR},
        ),
        # The author pushed/replied after the maintainer: back to us.
        (
            _state(
                last_author_activity=NOW - timedelta(hours=1),
                last_maintainer_activity=NOW - timedelta(days=1),
            ),
            {LABEL_AWAITING_MAINTAINER},
        ),
        # Draft, nobody has responded: no review label.
        (_state(is_draft=True), set()),
        # Draft, maintainer spoke last: still waiting on the author.
        (
            _state(
                is_draft=True,
                last_author_activity=NOW - timedelta(days=2),
                last_maintainer_activity=NOW - timedelta(days=1),
            ),
            {LABEL_AWAITING_AUTHOR},
        ),
        # Stale: waiting on the author for more than 30 days.
        (
            _state(
                last_author_activity=NOW - timedelta(days=40),
                last_maintainer_activity=NOW - timedelta(days=31),
            ),
            {LABEL_AWAITING_AUTHOR, LABEL_STALE},
        ),
        # Not stale if we're the ones sitting on it, however long.
        (
            _state(last_author_activity=NOW - timedelta(days=100)),
            {LABEL_AWAITING_MAINTAINER},
        ),
        # Unresolved AI review threads.
        (
            _state(open_bot_threads=2),
            {LABEL_AI_FEEDBACK_OPEN, LABEL_AWAITING_MAINTAINER},
        ),
        # Closed PRs keep whatever managed labels they had and gain nothing.
        (
            _state(
                is_open=False,
                labels={LABEL_CI_PASSING, "bug", "awaiting feedback"},
                open_bot_threads=3,
            ),
            {LABEL_CI_PASSING},
        ),
    ],
)
def test_compute_desired_labels(state: PRState, expected: set[str]) -> None:
    """The decision table."""
    assert compute_desired_labels(state) == expected


def test_label_diff_only_touches_managed_labels() -> None:
    """Unmanaged labels are never added or removed; legacy ones are removed."""
    state = _state(
        labels={"bug", "t-sql", "awaiting feedback", LABEL_CI_FAILING},
        ci_runs=_runs("success"),
    )
    to_add, to_remove = label_diff(state)
    assert to_add == {LABEL_CI_PASSING, LABEL_AWAITING_MAINTAINER}
    assert to_remove == {LABEL_CI_FAILING, "awaiting feedback"}


def test_label_diff_no_change() -> None:
    """Nothing to do when the labels are already right."""
    state = _state(labels={"bug", LABEL_AWAITING_MAINTAINER})
    assert label_diff(state) == (set(), set())


class _FakeClient:
    """Enough of GitHubClient for resolve_targets and ensure_labels."""

    def __init__(self, pages: dict[str, list[Any]]) -> None:
        self.pages = pages
        self.calls: list[tuple[str, str, Any]] = []

    def paginate(self, path: str, params: Any = None, key: str = "") -> Any:
        if path == "pulls":
            assert params == {"state": "open"}
        return iter(self.pages[path])

    def rest(self, method: str, path: str, body: Any = None, params: Any = None) -> Any:
        self.calls.append((method, path, body))
        return None


@pytest.mark.parametrize(
    "event_name,event,expected",
    [
        ("pull_request_target", {"pull_request": {"number": 7}}, [7]),
        ("pull_request_review", {"pull_request": {"number": 8}}, [8]),
        ("pull_request_review_thread", {"pull_request": {"number": 9}}, [9]),
        # Comment on a PR vs comment on a plain issue.
        ("issue_comment", {"issue": {"number": 10, "pull_request": {}}}, [10]),
        ("issue_comment", {"issue": {"number": 11}}, []),
        # workflow_run: look the PR up from the commit (fork PRs have an empty
        # pull_requests list in the payload).
        ("workflow_run", {"workflow_run": {"head_sha": "abc"}}, [12]),
        # Everything else sweeps all open PRs.
        ("schedule", {}, [20, 21]),
        ("workflow_dispatch", {"inputs": {}}, [20, 21]),
    ],
)
def test_resolve_targets(
    event_name: str, event: dict[str, Any], expected: list[int]
) -> None:
    """Each event maps to the right set of PRs."""
    client = _FakeClient(
        {
            "commits/abc/pulls": [
                {"number": 12, "state": "open"},
                {"number": 13, "state": "closed"},
            ],
            "pulls": [{"number": 20}, {"number": 21}],
        }
    )
    assert resolve_targets(client, event_name, event) == expected  # type: ignore


def test_ensure_labels() -> None:
    """Only missing labels are created, and only when applying."""
    client = _FakeClient({"labels": [{"name": LABEL_CI_PASSING}, {"name": "bug"}]})
    created = ensure_labels(client, apply=False)  # type: ignore
    assert LABEL_CI_PASSING not in created
    assert LABEL_CI_FAILING in created
    assert client.calls == []

    ensure_labels(client, apply=True)  # type: ignore
    assert len(client.calls) == len(created)
    assert all(
        method == "POST" and path == "labels" for method, path, _ in client.calls
    )


def test_ci_runs_for_sha_reports_first_run_time() -> None:
    """The earliest CI run's creation is the push time; re-runs don't move it."""

    class _Client:
        def rest(self, method: str, path: str, params: Any = None) -> Any:
            assert params["head_sha"] == "abc"
            return {
                "workflow_runs": [  # Newest first.
                    {
                        "name": "CI",
                        "event": "pull_request",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2026-10-16T10:00:00Z",
                    },
                    {
                        "name": "CI",
                        "event": "pull_request",
                        "status": "completed",
                        "conclusion": "failure",
                        "created_at": "2026-10-16T09:00:00Z",
                    },
                    {
                        "name": "Other",
                        "event": "pull_request",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2026-10-16T08:00:00Z",
                    },
                ]
            }

    runs, pushed_at = _ci_runs_for_sha(_Client(), "abc")  # type: ignore[arg-type]
    assert runs == [WorkflowRun("CI", "completed", "success")]
    assert pushed_at == datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc)
