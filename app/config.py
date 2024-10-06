# app/config.py

import json

# Load configuration from JSON file
with open("app/config.json", "r") as config_file:
    config = json.load(config_file)

REDIS_HOST = config["REDIS_HOST"]
REDIS_PORT = config["REDIS_PORT"]
REDIS_DB = config["REDIS_DB"]
