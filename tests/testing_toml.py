from pymatk.managers import BasicManager
import time

config = "basic_manager_test.toml"

man = BasicManager("testing_BM", config)

for i in range(10):
    print(man.all_values)
    time.sleep(1)
