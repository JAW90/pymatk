import logging
import time

from pymatk.managers import BasicManager
from pymatk.logging import logger

logger.setLevel(logging.DEBUG)

config = "test_config.toml"

man = BasicManager("testing_BM", config, debug=True, running=True)

time.sleep(5)

man.stop()
