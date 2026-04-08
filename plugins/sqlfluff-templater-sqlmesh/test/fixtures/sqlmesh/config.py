"""SQLMesh project configuration for test fixtures."""

from sqlmesh import Config

config = Config(
    model_defaults={
        "dialect": "duckdb",
    },
    default_gateway="local",
    gateways={
        "local": {
            "connection": {
                "type": "duckdb",
                "database": ":memory:",
            }
        }
    },
    variables={
        "start_date": "2023-01-01",
        "DEV": True,
        "model_name": "simple_model",
        "is_dev": True,
        "start_ds": "2023-01-01",
        "end_ds": "2023-01-02",
    },
)
