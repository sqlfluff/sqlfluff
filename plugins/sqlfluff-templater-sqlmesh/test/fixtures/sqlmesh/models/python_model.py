"""Example Python model for SQLMesh test fixtures."""

import typing as t
from sqlmesh import ExecutionContext, model


@model(
    "python_model",
    kind="full",
    cron="@daily",
    columns={"id": "int", "name": "varchar", "computed_value": "double"},
)
def execute(
    context: ExecutionContext,
    start: t.Optional[str] = None,
    end: t.Optional[str] = None,
    **kwargs: t.Any,
) -> t.Dict[str, t.Any]:
    """Execute the Python model."""

    # Fetch data from upstream model
    df = context.fetchdf("SELECT * FROM source_table")

    # Add computed column
    df["computed_value"] = df["id"] * 2.5

    return df
