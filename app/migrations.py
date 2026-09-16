from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade() -> None:
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
