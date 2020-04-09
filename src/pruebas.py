
import os
import yaml
from pathlib import Path

usr_dir = os.path.join(str(Path.home()), ".rita")
print(usr_dir)

with open(os.path.join(usr_dir, "conf", "path_parameters.yml")) as f:
    paths = yaml.safe_load(f)

bucket = paths["bucket"]

print(bucket)
