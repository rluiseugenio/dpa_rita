#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
from pathlib import Path

usr_dir = os.path.join(str(Path.home()), ".rita")

with open(os.path.join(usr_dir, "conf", "path_parameters.yml")) as f:
    paths = yaml.safe_load(f)

BUCKET = paths["bucket"]
MY_REGION = paths["region"]
MY_REGION2 = paths["region2"]
MY_PROFILE = paths["profile"]
MY_KEY = paths["key"]
MY_AMI = paths["ami"]
MY_VPC = paths["vpc"]
MY_GATEWAY = paths["gateway"]
MY_SUBNET = paths["subnet"]
MY_GROUP = paths["group"]
