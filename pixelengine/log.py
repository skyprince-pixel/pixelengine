"""PixelEngine logging — provides a shared logger instance."""
import logging

logger = logging.getLogger("pixelengine")

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
