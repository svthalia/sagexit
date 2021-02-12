FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE sagexit.settings.production
ENV PATH /root/.poetry/bin:${PATH}

ARG commit_hash="unknown commit hash"
ENV COMMIT_HASH=${commit_hash}

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

WORKDIR /sagexit/src/
COPY resources/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY poetry.lock pyproject.toml /sagexit/src/

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends postgresql-client xmlsec && \
    rm --recursive --force /var/lib/apt/lists/* && \
    \
    mkdir --parents /sagexit/src/ && \
    mkdir --parents /sagexit/log/ && \
    mkdir --parents /sagexit/static/ && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    poetry config --no-interaction --no-ansi virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev --extras "production"

COPY website /sagexit/src/website/
