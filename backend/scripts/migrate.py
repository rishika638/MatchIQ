import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from alembic import command
from alembic.config import Config

from app.core.database import engine


def migrate():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    config = Config("alembic.ini")
    if "users" in table_names and "alembic_version" not in table_names:
        print("Existing application schema detected; stamping Alembic revision.")
        command.stamp(config, "head")
    else:
        print("Running Alembic migrations.")
        command.upgrade(config, "head")


if __name__ == "__main__":
    migrate()
