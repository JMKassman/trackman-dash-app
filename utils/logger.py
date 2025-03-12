import logging

# Configure logging with a custom format
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(name)s %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
__parent_logger = logging.getLogger("golf-analysis")


def get_child_logger(name: str) -> logging.Logger:
    return __parent_logger.getChild(name)


def set_parent_log_level(level: int) -> None:
    """Use the constants in the logging module to set the log level for the parent logger"""
    __parent_logger.setLevel(level)
