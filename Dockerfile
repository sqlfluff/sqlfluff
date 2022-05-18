FROM python:3.9-slim-bullseye

# Set separate working directory for easier debugging.
WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV /app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH $VIRTUAL_ENV/bin:$PATH
RUN pip install --upgrade pip setuptools wheel

# Install requirements seperately
# to take advantage of layer caching.
# N.B. we extract the requirements from setup.cfg
COPY setup.cfg .
RUN python -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); print(c['options']['install_requires'])" > requirements.txt
RUN pip install --upgrade -r requirements.txt

# Copy minimal set of SQLFluff package files.
COPY MANIFEST.in .
COPY README.md .
COPY setup.py .
COPY src ./src

# Install sqlfluff package.
RUN pip install --no-dependencies .

# Switch to non-root user.
USER 5000

# Switch to new working directory as default bind mount location.
# User can bind mount to /sql and not have to specify the full file path in the command:
# i.e. docker run --rm -it -v $PWD:/sql sqlfluff/sqlfluff:latest lint test.sql
WORKDIR /sql

# Set SQLFluff command as entry point for image.
ENTRYPOINT ["sqlfluff"]
CMD ["--help"]
