FROM python:3.9-slim-bullseye

# Set separate working directory for easier debugging.
WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV .venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH $VIRTUAL_ENV/bin:$PATH
RUN pip install --upgrade pip setuptools wheel

# Install requirements seperately
# to take advantage of layer caching.
COPY requirements.txt .
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

# Set SQLFluff command as entry point for image.
ENTRYPOINT ["sqlfluff"]
CMD ["--help"]
