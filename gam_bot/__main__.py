from gam_bot import settings
from .logs import setup_logging


setup_logging()

from .bot import Bot


def main() -> None:
    Bot().run(settings.DISCORD_KEY)


if __name__ == "__main__":
    main()
