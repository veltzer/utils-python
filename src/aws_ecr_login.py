#!/usr/bin/env python

import os
import sys
import json

prog = sys.argv[0]
if len(sys.argv) != 3:
    print(f"usage: {prog} ENV_REGION ENV_ACCOUNT_ID")
    sys.exit(1)

ENV_REGION = sys.argv[1]
ENV_ACCOUNT_ID = sys.argv[2]

filename = os.path.expanduser("~/.docker/config.json")
with open(filename) as file_handle:
    config = json.load(file_handle)
ecr_url = f"{ENV_ACCOUNT_ID}.dkr.ecr.{ENV_REGION}.amazonaws.com"
if ecr_url in config["auths"]:
    sys.exit()
print(f"{prog}: logging in to docker")
cmd = f"aws ecr get-login-password --region \"{ENV_REGION}\"\
    | docker login --username AWS --password-stdin \"{ecr_url}\" > /dev/null"
# print(f"cmd is {cmd}")
os.system(cmd)
