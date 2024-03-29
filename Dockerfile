FROM python:3.10 as just-python
RUN apt-get update


FROM just-python as build-image
# Use a non-root user
RUN useradd -ms /bin/bash build
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
RUN /venv/bin/pip install wheel==0.37.0
RUN ./tools_venv/bin/pip install wheel==0.37.0 poetry==1.6.1

# Build and install dependencies to the output virtualenv first so we don't have to re-do it when the dependencies do not change
COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml
RUN ./tools_venv/bin/poetry export --with release --without dev -f 'requirements.txt' -o ./requirements.txt --without-hashes
RUN PATH=/home/build/tools_venv/bin:$PATH /venv/bin/pip install -r ./requirements.txt
RUN ./tools_venv/bin/pip install poetry-dynamic-versioning==0.13.1

# Copy in all source code so we can build the wheel
COPY --chown=build:users . ./src/
WORKDIR ./src/
RUN PATH=/home/build/tools_venv/bin:$PATH ../tools_venv/bin/poetry build

# Install in the output virtualenv, which will eventually be copied to the final image
RUN PATH=/home/build/tools_venv/bin:$PATH /venv/bin/pip install ./dist/*.whl


FROM just-python as runtime-image
RUN useradd -ms /bin/bash run
COPY --from=build-image --chown=run:users /venv /venv
USER run:users
# Configure environment to run
ENV PATH=/venv/bin:$PATH
ENV DJANGO_SETTINGS_MODULE=gam.settings.deployment
ENTRYPOINT manage migrate && manage run_discord_bot