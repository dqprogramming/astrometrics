# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.13-slim-bookworm AS python

FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app
ARG UID=1000
ARG GID=1000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY ./entrypoint.sh /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# create a non-root user matching the host UID/GID
RUN groupadd -g ${GID} appuser && \
    useradd -u ${UID} -g ${GID} -m appuser

WORKDIR ${APP_HOME}

EXPOSE 443

# install dependencies into system Python via pip (for PyCharm compatibility)
COPY pyproject.toml uv.lock ${APP_HOME}/
RUN uv pip install --system -r pyproject.toml && \
    uv pip install --system --group dev

# copy application code to WORKDIR
COPY . ${APP_HOME}

RUN mkdir -p ${APP_HOME}/.venv && \
    chown -R appuser:appuser ${APP_HOME}

USER appuser

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
