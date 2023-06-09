FROM python:3.10.8

# never run a root-container
RUN useradd -m lizard

# set the working directory in the container
WORKDIR /home/lizard

RUN python3 -m pip install --upgrade pip poetry
USER lizard

# installation of dependecies is done before copying the code to leverage Docker layer caching
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-interaction --no-ansi

COPY ./backend ./backend
COPY ./scripts ./scripts
# COPY ./.git ./.git
EXPOSE 8000

# sleep of 10 is needed such that the DB is really read (needs some time post container start up)
CMD sleep 10 && poetry run scripts/run_db_migrations.sh -p && poetry run python -m uvicorn backend.application:app --host 0.0.0.0 --port 8000
