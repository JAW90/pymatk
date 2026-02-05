from pymatk.managers import BasicManager
import time

config = "test_config.toml"

man = BasicManager("testing_BM", config, debug=True, running=True)

time.sleep(5)

man._running = False
