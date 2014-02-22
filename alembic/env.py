from __future__ import with_statement
import sys, os
# append project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")))

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from vircu.models import db
from vircu.application import create_app

app = create_app(False)
target_metadata = db.Model.metadata

# more config
config.set_section_option('alembic', 'sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # changed this to use our DB object because of some issues with sqlalch
    connection = db.engine.connect()
    
    context.configure(
                compare_type=True,
                connection=connection,
                target_metadata=target_metadata
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

