FROM dhi.io/python:3.14-debian13-dev AS build

WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN pip install --no-cache-dir --upgrade pip setuptools wheel pip-tools

# N.B. we extract the requirements from pyproject.toml
COPY pyproject.toml .
# Use piptools to extract requirements from pyproject.toml as described in
# https://github.com/pypa/pip/issues/11584
RUN pip-compile -o requirements.txt pyproject.toml -v --strip-extras
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy minimal set of SQLFluff package files.
COPY MANIFEST.in .
COPY README.md .
COPY src ./src

# Install sqlfluff package.
RUN pip install --no-cache-dir --no-dependencies .

FROM dhi.io/python:3.14-debian13
# OCI annotations
LABEL org.opencontainers.image.title="sqlfluff" \
      org.opencontainers.image.authors="sqlfluff Community" \
      org.opencontainers.image.description="A modular SQL linter and auto-formatter with support for multiple dialects and templated code" \
      org.opencontainers.image.source="https://github.com/sqlfluff/sqlfluff" \
      org.opencontainers.image.documentation="https://docs.sqlfluff.com/en/stable/"

COPY --from=build /app/.venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv PATH=/app/.venv/bin:$PATH

# Switch to new working directory as default bind mount location.
# User can bind mount to /sql and not have to specify the full file path in the command:
# i.e. docker run --rm -it -v $PWD:/sql sqlfluff/sqlfluff:latest lint test.sql
WORKDIR /sql

# Set SQLFluff command as entry point for image.
ENTRYPOINT ["sqlfluff"]
CMD ["--help"]
