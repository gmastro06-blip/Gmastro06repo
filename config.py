# config.py - Create this new file in the root directory
import json
import logging

logging.basicConfig(filename='logs/bot_log.txt', level=logging.DEBUG)

def load_config(file='config.json'):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        logging.info("Config loaded successfully")
        return data
    except FileNotFoundError:
        logging.error(f"Config file not found: {file}")
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON in config file")
        raise