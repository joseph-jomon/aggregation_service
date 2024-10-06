import json
import os

# Define the path to the config file (assuming it's inside the config folder)
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

# Load the config file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Make the Redis settings accessible
REDIS_HOST = config.get("REDIS_HOST", "localhost")
REDIS_PORT = config.get("REDIS_PORT", 6379)
REDIS_DB = config.get("REDIS_DB", 0)
