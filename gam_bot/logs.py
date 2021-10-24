from logging import DEBUG, basicConfig


def setup_logging() -> None:
    basicConfig(
        level=DEBUG,
        format='%(levelname)s %(asctime)s [%(name)s] (%(process)d) %(message)s'
    )