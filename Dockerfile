# Pinned because a floating tag changed underneath us and broke the build. To update, take the
# tag and digest of a newer python:3.12.x-alpine3.y image from Docker Hub.
FROM python:3.12.16-alpine3.24@sha256:e6dae589c1c05976188fd3bd019afd091445fc533ed2ea29001beddc7368a9c8 AS just-python
RUN apk upgrade --no-cache
# Needed for both build and deploy
RUN apk add --no-cache libpq

FROM just-python AS build-image
# build-only deps
RUN apk add --no-cache gcc musl-dev postgresql-dev
# Use a non-root user
RUN adduser  -S build
RUN mkdir /venv
RUN chown -R build:users /venv
USER build:users
WORKDIR /home/build/

# Need two virtual environments - one for tools (poetry, cmake, etc) and one for running
RUN python3 -m venv /venv
RUN python3 -m venv ./tools_venv
# We always want the latest pip, but the rest of our build dependencies should be locked.
RUN /venv/bin/pip install -U pip
RUN ./tools_venv/bin/pip install -U pip
RUN /venv/bin/pip install wheel
RUN ./tools_venv/bin/pip install wheel poetry==1.8.3
RUN ./tools_venv/bin/poetry self add "poetry-plugin-export@~1.8"
RUN ./tools_venv/bin/poetry config warnings.export false

# Build and install dependencies to the output virtualenv first so we don't have to re-do it when the dependencies do not change
COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml
RUN ./tools_venv/bin/poetry export --with release --without dev -f 'requirements.txt' -o ./requirements.txt --without-hashes
RUN PATH=/home/build/tools_venv/bin:$PATH /venv/bin/pip install -r ./requirements.txt

# Copy in all source code so we can build the wheel
COPY --chown=build:users ./src ./src
ARG APP_VERSION=0.0.0
RUN sed -i -e "s/v0.0.0/v${APP_VERSION}/g" pyproject.toml
RUN PATH=/home/build/tools_venv/bin:$PATH ./tools_venv/bin/poetry build

# Install in the output virtualenv, which will eventually be copied to the final image
RUN PATH=/home/build/tools_venv/bin:$PATH /venv/bin/pip install ./dist/*.whl


FROM just-python AS runtime-image
RUN adduser -S run
COPY --from=build-image --chown=run:users /venv /venv
# Configure environment to run
ENV PATH=/venv/bin:$PATH
ENV DJANGO_SETTINGS_MODULE=gam.settings.deployment
ENV STATIC_ROOT=/static
# Build the static files into the image so the web container can serve them itself.
# These values only let the settings load. collectstatic never connects to the database.
RUN SECRET_KEY=build-only DB_NAME=build-only DB_USER=build-only DB_PASSWORD=build-only \
    DB_HOST=build-only DB_PORT=5432 ALLOWED_HOST=build-only manage collectstatic --no-input
USER run:users
ENTRYPOINT ["manage", "migrate", "&&", "manage", "run_discord_bot"]