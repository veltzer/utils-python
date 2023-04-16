#!/usr/bin/env python

"""
This script outputs the url for pip to be used when logging in to aws codeartifact.

https://docs.aws.amazon.com/codeartifact/latest/ug/npm-auth.html

Here is an example response:
    $ aws codeartifact login --tool npm --repository "$ENV_NPM_REPOSITORY" --domain "$ENV_DOMAIN"
        --domain-owner "$ENV_DOMAIN_OWNER"
"""

import os
import os.path
import sys
import datetime
import boto3
from furl import furl
import pyapikey

KEY = "codeartifact_npm_config"
USE_ENV = False
WRITE_FILE = True

prog = sys.argv[0]
if len(sys.argv) != 4:
    print(f"usage: {prog} ENV_DOMAIN ENV_DOMAIN_OWNER ENV_NPM_REPOSITORY")
    sys.exit(1)

ENV_DOMAIN = sys.argv[1]
ENV_DOMAIN_OWNER = sys.argv[2]
ENV_NPM_REPOSITORY = sys.argv[3]


def handle_data(url: str, short_url: str, password: str, replace: bool) -> None:
    """ really handle the data """
    if USE_ENV:
        url = furl(url)
        url.username = USERNAME  # type: ignore
        url.password = password  # type: ignore
        url.path.add("simple/")  # type: ignore
        print(f"export CODEARTIFACT_AUTH_TOKEN={password}")
        print(f"export npm_config_registry=\"{url}\"")
        print(f"export npm_config_{url}:always_auth=true")
        print("export npm_config_always_auth=true")
        print(f"export npm_config_{url}:_authToken={password}")
        print(f"export npm_config__authToken=\"{password}\"")
    if WRITE_FILE:
        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".npmrc")
        if not os.path.isfile(filename) or replace:
            with open("/dev/tty", "wt", encoding="utf-8") as stream:
                print(f"Writing new file [{filename}]...", file=stream)
            with open(filename, "wt", encoding="utf-8") as stream:
                stream.write(f"{short_url}:_authToken={password}\n")
                stream.write(f"registry={url}\n")


temp_store = pyapikey.core.TempStore()
if temp_store.has(KEY):
    data = temp_store.get(KEY)
    expiration = data["expiration"]
    now = datetime.datetime.now()
    if expiration > now:
        d_url = data["url"]
        d_short_url = data["short_url"]
        d_password = data["password"]
        handle_data(url=d_url, short_url=d_short_url, password=d_password, replace=False)
        sys.exit()

with open("/dev/tty", "wt", encoding="utf-8") as f:
    print("Creating new temp key for codeartifact npm", file=f)

client = boto3.client('codeartifact')
res = client.get_authorization_token(
    domain=ENV_DOMAIN,
    domainOwner=ENV_DOMAIN_OWNER,
    durationSeconds=43200,
)
d_password = res["authorizationToken"]
expiration = res["expiration"]
USERNAME = "aws"
res = client.get_repository_endpoint(
    domain=ENV_DOMAIN,
    domainOwner=ENV_DOMAIN_OWNER,
    repository=ENV_NPM_REPOSITORY,
    format="npm",
)
d_url = res["repositoryEndpoint"]
if d_url.startswith("https:"):
    d_short_url = d_url[6:]

data = {}
data["url"] = d_url
data["short_url"] = d_short_url
data["password"] = d_password
data["expiration"] = expiration.replace(tzinfo=None)
temp_store.set(KEY, data)
temp_store.save()

handle_data(url=d_url, short_url=d_short_url, password=d_password, replace=True)
