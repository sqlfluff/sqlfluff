ARG PROD_IMAGE=dhi.io/python:3.14-debian13
ARG BASE_IMAGE=dhi.io/python:3.14-debian13-dev

FROM ${BASE_IMAGE} AS build

WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN python -m venv "${VIRTUAL_ENV}" \
 && pip install --no-cache-dir --upgrade pip setuptools wheel pip-tools

COPY pyproject.toml .
# Use piptools to extract requirements from pyproject.toml as described in
# https://github.com/pypa/pip/issues/11584
RUN pip-compile -o requirements.txt pyproject.toml -v --strip-extras \
 && pip install --no-cache-dir --upgrade -r requirements.txt

# Copy minimal set of SQLFluff package files.
COPY MANIFEST.in README.md .
COPY src ./src
# Install sqlfluff package.
RUN pip install --no-cache-dir --no-dependencies .


# production image
FROM ${PROD_IMAGE} AS prod
# OCI annotations
LABEL org.opencontainers.image.title="sqlfluff" \
      org.opencontainers.image.authors="sqlfluff Community" \
      org.opencontainers.image.description="A modular SQL linter and auto-formatter with support for multiple dialects and templated code" \
      org.opencontainers.image.source="https://github.com/sqlfluff/sqlfluff" \
      org.opencontainers.image.documentation="https://docs.sqlfluff.com/en/stable/"

COPY --from=build /app/.venv /app/.venv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Switch to new working directory as default bind mount location.
# User can bind mount to /sql and not have to specify the full file path in the command:
# i.e. docker run --rm -it -v $PWD:/sql sqlfluff/sqlfluff:latest lint test.sql
WORKDIR /sql

ENTRYPOINT ["sqlfluff"]
CMD ["--help"]


# development image
FROM ${BASE_IMAGE} AS dev

COPY --from=build /app/.venv /app/.venv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /sql
ENTRYPOINT ["sqlfluff"]
CMD ["--help"]