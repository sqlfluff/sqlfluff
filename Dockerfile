FROM python:3.10-slim-bullseye

COPY src ./src
COPY setup.py .
COPY README.md .

RUN pip install --upgrade pip
RUN pip install .

USER 5000

ENTRYPOINT ["sqlfluff"]

CMD ["--help"]
