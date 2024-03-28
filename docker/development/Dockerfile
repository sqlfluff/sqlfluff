FROM python:3.9

# Set separate working directory for easier debugging.
WORKDIR /app
ENV PYTHONPATH=/app;/app/src

# Install Git
RUN apt-get -y update
RUN apt-get -y install git

COPY requirements.txt /requirements.txt
COPY requirements_dev.txt /requirements_dev.txt

#Install Dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements.txt --upgrade --default-timeout=100
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements_dev.txt --upgrade --default-timeout=100

# Set up dbt-related dependencies.
RUN --mount=type=cache,target=/root/.cache/pip pip install dbt-postgres
# N.B. we extract the requirements from plugins/sqlfluff-templater-dbt/setup.cfg,
# filtering out sqlfluff itself, to prevent it from being installed as a package.
# (Below, we install it in editable mode.)
COPY plugins/sqlfluff-templater-dbt/setup.cfg /tmp
RUN python -c "import configparser; c = configparser.ConfigParser(); c.read('/tmp/setup.cfg'); print(c['options']['install_requires'])" | grep -v sqlfluff > /tmp/dbt-requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade -r /tmp/dbt-requirements.txt

# Copy everything. (Note: If needed, we can use .dockerignore to limit what's copied.)
COPY . .

# Install sqlfluff and the dbt templater in editable mode.
RUN pip install --no-dependencies -e . -e plugins/sqlfluff-templater-dbt
