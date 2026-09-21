import logging
import sys

logger = logging.getLogger("sra_leads")


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging for SRA Business Lead Finder."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    return logger
