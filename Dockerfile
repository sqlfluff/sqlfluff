FROM python:3.9-slim-bullseye

# Set separate working directory for easier debugging.
WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV /app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH $VIRTUAL_ENV/bin:$PATH
RUN pip install --no-cache-dir --upgrade pip setuptools wheel pip-tools

# Install requirements separately
# to take advantage of layer caching.
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

# Switch to non-root user.
USER 5000

# Switch to new working directory as default bind mount location.
# User can bind mount to /sql and not have to specify the full file path in the command:
# i.e. docker run --rm -it -v $PWD:/sql sqlfluff/sqlfluff:latest lint test.sql
WORKDIR /sql

# Set SQLFluff command as entry point for image.
ENTRYPOINT ["sqlfluff"]
CMD ["--help"]
