import logging
from typing import Union

# Global log level, defaults to INFO
LOG_LEVEL = logging.INFO

def init_logging(level: Union[int, str] = None) -> None:
    """Initialize logging with a specific format and level.
    
    Args:
        level: Optional logging level to override the global LOG_LEVEL
    """
    global LOG_LEVEL
    if level is not None:
        LOG_LEVEL = level
    
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Ensure configuration is applied even if logging was initialized elsewhere
    )

def set_log_level(level: Union[int, str]) -> None:
    """Set the global logging level.
    
    Args:
        level: New logging level to use (e.g., logging.DEBUG, logging.INFO, etc.)
    """
    global LOG_LEVEL
    LOG_LEVEL = level
    logging.getLogger().setLevel(level)

# Initialize logging with default settings
init_logging() 