FROM python:3.9-slim-bullseye

# Copy minimal set of SQLFluff install files
# into their own folder for easier debugging.
WORKDIR /app
COPY src ./src
COPY setup.py .
COPY MANIFEST.in .
COPY README.md .

# Install SQLFluff in virtual environment to
# avoid potential clashes with system dependencies.
RUN python -m venv .venv \
    && . .venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install .

# Create unpriveleged user.
USER 5000

# Set SQLFluff command as the the entry point for image.
ENTRYPOINT ["/app/.venv/bin/sqlfluff"]
CMD ["--help"]
