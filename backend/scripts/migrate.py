import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config


def run_upgrade() -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")


async def main() -> None:
    await asyncio.to_thread(run_upgrade)
    print("Migration completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
