"""CampusTask — 校园任务清单"""

import logging

__version__ = "0.3.0"

logging.basicConfig(
    filename="campus_task.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
