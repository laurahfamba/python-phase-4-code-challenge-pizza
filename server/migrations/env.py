import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# Retrieve the Alembic configuration object, which gives access
# to the values within the .ini file in use.
config = context.config

# Interpret the configuration file for Python logging.
# This line sets up loggers as per the configuration.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_database_engine():
    try:
        # This works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except TypeError:
        # This works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_database_url():
    try:
        return get_database_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_database_engine().url).replace('%', '%%')


# Add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_database_url())
database = current_app.extensions['migrate'].db

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(database, 'metadatas'):
        return database.metadatas[None]
    return database.metadata


def run_migrations_offline():
    """Execute migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Execute migrations in 'online' mode.

    In this mode we need to create an Engine and associate
    a connection with the context.
    """

    # Callback to prevent auto-migration generation when there are no schema changes.
    # Reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    engine = get_database_engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine if Alembic is running in 'offline' mode or 'online' mode and execute accordingly.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
