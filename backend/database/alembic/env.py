import os
import sys

import git

# Python cannot import from parent modules if executed in this directory if
# the path is not present in the PYTHONPATH --> append repo root
# see https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
current_dir = os.path.dirname(os.path.realpath(__file__))
git_repo = git.Repo(current_dir, search_parent_directories=True)
git_root = git_repo.git.rev_parse("--show-toplevel")
sys.path.append(git_root)

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import backend.database.models  # noqa : needs to be imported to allow auto migration creation
from backend.database import Base, database_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", str(database_url(async_connection=False)))
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
