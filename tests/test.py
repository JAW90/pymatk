import logging
import time

from pymatk.managers import SimpleManager
from pymatk.logging import logger
# from pymatk.controllers import TestController

logger.setLevel(logging.DEBUG)

config = "test_config.toml"

man = SimpleManager("testing_SM", config, running=False)

# tc = TestController("testing_SC", running=True)

# tc.connect_to_rack(man.instrument_rack)

# tc.configure_input("TIME_KEEPER", "time")

# tc.configure_output("RANDOMGEN", "set_parameter")

man.start()

time.sleep(5)

man.stop()
