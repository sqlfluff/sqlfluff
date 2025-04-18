FROM python:3.12

# Set separate working directory for easier debugging.
WORKDIR /app
ENV PYTHONPATH=/app;/app/src

# Install Git
RUN apt-get -y update
RUN apt-get -y install git

COPY requirements_dev.txt /requirements_dev.txt

#Install Dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements_dev.txt --upgrade --default-timeout=100

# Set up dbt-related dependencies.
RUN --mount=type=cache,target=/root/.cache/pip pip install dbt-postgres

# Copy everything. (Note: If needed, we can use .dockerignore to limit what's copied.)
COPY . .

# Install sqlfluff and the dbt templater in editable mode.
RUN pip install -e . -e plugins/sqlfluff-templater-dbt

